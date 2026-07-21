"""Views for the imports app — upload, preview, confirm, history."""

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from core.models import log_activity, get_client_ip
from expenses.models import Category, Expense, Wallet
from notifications.models import create_notification

from .forms import UploadForm
from .models import ImportedFile, ImportTransaction
from .services.csv_parser import parse_csv_file
from .services.pdf_parser import parse_pdf_file


class ImportUploadView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "imports/import.html"

    def get(self, request):
        return render(request, self.template_name, {"form": UploadForm()})

    def post(self, request):
        form = UploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        upload = request.FILES["file"]
        name = upload.name.lower()
        bank_name = request.POST.get("bank_name", "")

        if name.endswith(".csv"):
            rows = parse_csv_file(upload)
            file_type = "csv"
        elif name.endswith(".pdf"):
            rows = parse_pdf_file(upload)
            file_type = "pdf"
        else:
            messages.error(
                request, "Unsupported file type. Please upload a PDF or CSV.")
            return render(request, self.template_name, {"form": UploadForm()})

        if not rows:
            messages.warning(
                request, "No transactions could be extracted from this file. Try a different file or add transactions manually.")
            return render(request, self.template_name, {"form": UploadForm()})

        imported_file = ImportedFile.objects.create(
            user=request.user, file_type=file_type, bank_name=bank_name,
            file_name=upload.name, row_count=len(rows), status="processing",
        )

        request.session["import_rows"] = rows
        request.session["import_file_name"] = upload.name
        request.session["import_file_type"] = file_type
        request.session["import_file_id"] = imported_file.id

        # Debugging line
        print(
            f"Uploaded file: {upload.name}, type: {file_type}, rows extracted: {len(rows)}")

        log_activity(request.user, "upload_import", "imports",
                     f"Uploaded {upload.name} ({len(rows)} rows)", ip_address=get_client_ip(request))

        categories = list(Category.objects.filter(
            user=request.user).values("id", "name"))
        wallets = list(Wallet.objects.filter(
            user=request.user, is_active=True).values("id", "name"))
        return render(request, "imports/import_preview.html", {"rows": rows, "categories": categories, "wallets": wallets, "file_name": upload.name})


class ImportConfirmView(LoginRequiredMixin, View):
    login_url = "users:login"

    def post(self, request):
        raw_rows = request.session.get("import_rows", [])
        if not raw_rows:
            return redirect("imports:upload")

        confirmed_rows = []
        indices = request.POST.getlist("row_index")
        # Debugging line
        print(
            f"Received indices for confirmation: {indices}, raw rows: {raw_rows}")
        for idx_str in indices:
            idx = int(idx_str)
            if idx >= len(raw_rows):
                continue
            row = raw_rows[idx]
            row["category"] = request.POST.get(f"category_{idx}", "")
            row["wallet"] = request.POST.get(f"wallet_{idx}", "")
            row["transaction_type"] = request.POST.get(
                f"type_{idx}", row["transaction_type"])
            confirmed_rows.append(row)

        if not confirmed_rows:
            messages.info(request, "No rows were selected for import.")
            return redirect("imports:upload")

        expenses_to_create = []
        category_cache = {}
        for row in confirmed_rows:
            try:
                amount = float(str(row["amount"]).replace(",", ""))
            except (ValueError, TypeError):
                continue
            if amount <= 0:
                continue
            try:
                date_obj = datetime.strptime(
                    str(row["date"])[:10], "%Y-%m-%d").date()
            except ValueError:
                try:
                    date_obj = datetime.strptime(
                        str(row["date"])[:10], "%d/%m/%Y").date()
                except ValueError:
                    try:
                        date_obj = datetime.strptime(
                            str(row["date"])[:10], "%m/%d/%Y").date()
                    except ValueError:
                        continue

            cat = None
            cat_id = row.get("category")
            if cat_id:
                if cat_id not in category_cache:
                    try:
                        category_cache[cat_id] = Category.objects.get(
                            id=cat_id, user=request.user)
                    except Category.DoesNotExist:
                        category_cache[cat_id] = None
                cat = category_cache[cat_id]

            wallet_id = row.get("wallet")
            wallet = None
            if wallet_id:
                wallet = Wallet.objects.filter(
                    id=wallet_id, user=request.user, is_active=True).first()
            if not wallet:
                wallet = Wallet.objects.filter(
                    user=request.user, is_active=True).order_by("id").first()
                if not wallet:
                    messages.error(
                        request, "Please create at least one wallet before importing transactions.")
                    return redirect("expenses:wallet_add")

            source = "csv" if request.session.get(
                "import_file_type") == "csv" else "pdf"
            expenses_to_create.append(Expense(
                user=request.user, wallet=wallet, amount=amount, date=date_obj, category=cat,
                description=row.get("description", "")[:200],
                transaction_type=row.get("transaction_type", "expense"), source=source,
            ))

        created = Expense.objects.bulk_create(expenses_to_create)

        file_id = request.session.get("import_file_id")
        if file_id:
            ImportedFile.objects.filter(id=file_id).update(
                row_count=len(created), status="completed")

        create_notification(request.user, "Import Complete",
                            f"Successfully imported {len(created)} transactions from {request.session.get('import_file_name', 'your file')}.", "import")

        log_activity(request.user, "confirm_import", "imports",
                     f"Imported {len(created)} transactions", ip_address=get_client_ip(request))

        for key in ("import_rows", "import_file_name", "import_file_type", "import_file_id"):
            request.session.pop(key, None)

        messages.success(
            request, f"Successfully imported {len(created)} transactions!")
        return redirect("expenses:list")


class ImportHistoryView(LoginRequiredMixin, View):
    login_url = "users:login"
    template_name = "imports/import_history.html"

    def get(self, request):
        files = ImportedFile.objects.filter(
            user=request.user).order_by("-uploaded_at")
        return render(request, self.template_name, {"files": files})
