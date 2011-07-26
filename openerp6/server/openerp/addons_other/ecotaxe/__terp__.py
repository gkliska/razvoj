{
	"name" : "Module for 'Eco participation'",
	"version" : "1.0",
	"author" : "Sednacom",
	"category" : "Generic Modules/Others",
	"website": "http://www.sednacom.fr",
	"module": "",
	"description": """'Eco participation' management

This module adds the management of 'Eco participation' in TinyERP.

'Eco participation', mostly known as 'Ecotaxe', is a french specificity; its purpose is to finance recycling of products with a high cost of treatment.

Install this module if you need to manage 'Eco participation' in your business.

Module features:
 - amount of 'Eco participation' for product by producer
 - 'Eco participation' management in sale orders, purchases orders and invoices.

	""",
	"depends" : ["base","product","sale","purchase","l10n_fr"],
	"init_xml" : [],
	"update_xml" : ["ecotaxe_view.xml"],
	"demo_xml" : [], 
	"active": False,
	"installable": True
}
