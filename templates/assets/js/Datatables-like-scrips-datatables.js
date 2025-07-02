let x = new RdataTB('myTable',{
		// RenderJSON:[], // Convert Json to Table html 
		ShowSearch:true, // show search field,
		ShowSelect:true, // show show select,
		ShowPaginate:true, // show paginate ,
		SelectionNumber:[5,10,20,50], //Change Option in Select
		HideColumn:[], // Hide column
		ShowHighlight:false, // show Highlight if search
	        fixedTable:true, // fixed table
                sortAnimate:true // show animated if sorted
		// ExcludeColumnExport:[] 
	});