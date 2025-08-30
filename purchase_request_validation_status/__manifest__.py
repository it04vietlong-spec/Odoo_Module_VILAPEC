{
    "name": "Purchase Request Validation Status",
    "version": "1.0",
    "summary": "Thêm cột trạng thái và này validate cho Purchase Request",
    "category": "Purchase Management",
    "author": "Vuongtv",
    # "author": "0214",
    "depends": ["purchase_request", "base_tier_validation"],
    "data": [
        "views/purchase_request_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
