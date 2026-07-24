# 🔥 GRN DOWNLOAD API (ACT B2B ONLY)
@app.route("/get-grn", methods=["GET"])
def get_grn():

    try:

        # -----------------------
        # ACT B2B ACCOUNT
        # -----------------------

        account = {
            "cred": "act@swissmilitaryindia.com",
            "password": "Swiss@123",
            "seller_id": "80000332",
            "warehouse_id": "600040",
            "user_id": "300000000462"
        }

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
            f"&generated_by=Automation"
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

        res = requests.get(grn_url, headers=headers)

        return Response(
            res.text,
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
