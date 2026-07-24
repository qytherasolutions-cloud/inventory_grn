from flask import Flask, request, jsonify, Response
import requests
from datetime import datetime, timedelta
import csv
import io

app = Flask(__name__)

# 🔥 MULTI WAREHOUSE CONFIG
ACCOUNTS = {

    "RATAN": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000493",
        "warehouse_id": "600071",
        "user_id": "300000000850"
    },

    "ACT B2B": {
        "cred": "act@swissmilitaryindia.com",
        "password": "Swiss@123",
        "seller_id": "80000332",
        "warehouse_id": "600040",
        "user_id": "300000000462"
    },

    "RETAIL": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000333",
        "warehouse_id": "600040",
        "user_id": "300000000850"
    },

    "MUMBAI": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000329",
        "warehouse_id": "600044",
        "user_id": "300000000850"
    },

    "Nelamangala": {
        "cred": "sanjay.mahto@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000476",
        "warehouse_id": "600049",
        "user_id": "300000000850"
    }

}


@app.route("/")
def home():
    return "GRN Automation Running 🚀"


# 🔥 GRN DOWNLOAD API
@app.route("/get-grn", methods=["GET"])
def get_grn():

    try:

        # -----------------------
        # GET WAREHOUSE
        # -----------------------

        warehouse = request.args.get("warehouse")

        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # -----------------------
        # LOGIN
        # -----------------------

        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(
            login_url,
            json=login_payload,
            headers=login_headers
        )

        pim_sid = login_res.headers.get("pim-sid")

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login Failed"
            })

        # -----------------------
        # LAST 3 DAYS
        # -----------------------

        today = datetime.today()

        from_date = (today - timedelta(days=3)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        # -----------------------
        # GRN CSV URL
        # -----------------------

        grn_url = (
            "https://edge-service.emizainc.com/"
            "procurement/api/v1/good-received-notes/report/csv?"
            f"seller_id={account['seller_id']}"
            "&generated_by=Automation"
            f"&from={from_date}"
            f"&to={to_date}"
            "&filterBy=grn_created_at"
            "&reportType=grn_report"
            "&filter=created_at"
            f"&warehouseId={account['warehouse_id']}"
        )

        headers = {
            "accept": "application/json, text/plain, */*",
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-source": "SELLER",
            "x-tenant-id": "1",
            "x-user-id": account["user_id"],
            "x-warehouse-id": account["warehouse_id"]
        }

        # -----------------------
        # DOWNLOAD CSV
        # -----------------------

        res = requests.get(grn_url, headers=headers)

        # Read CSV
        input_csv = io.StringIO(res.text)
        reader = csv.reader(input_csv)
        rows = list(reader)
        
        if rows:
        
            header = rows[0]
        
            # Remove "Visual Qc Repairable" column
            if "Visual Qc Repairable" in header:
        
                remove_index = header.index("Visual Qc Repairable")
        
                for row in rows:
                    if len(row) > remove_index:
                        row.pop(remove_index)
        
                # Refresh header
                header = rows[0]
        
            # Format GRN Date
            if "GRN Date" in header:
        
                date_index = header.index("GRN Date")
        
                for row in rows[1:]:
        
                    if len(row) > date_index and row[date_index]:
        
                        try:
                            dt = datetime.strptime(
                                row[date_index],
                                "%d-%m-%Y %I:%M %p"
                            )
        
                            row[date_index] = dt.strftime("%d/%m/%Y")
        
                        except ValueError:
                            pass
        
        # Convert CSV back
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerows(rows)
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=grn_report.csv"
            }
        )

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
