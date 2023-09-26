{
    "name": "Purchase Order Lines Import",
    "summary": """
        Purchase Order Lines Import Module

        (Government Transactional Purchase Portal Integration)
        """,
    "author": "José López, OPTIC",
    "website": "https://optic.gob.do",
    "category": "Purchases",
    "version": "14.0.1.0.0",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_order_lines.xml",
        "views/purchase_views.xml",
    ],
    "installable": True,
}
