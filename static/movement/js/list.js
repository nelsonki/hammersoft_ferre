var tblSale;
$(function () {

    tblSale = $('#example').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        "ordering": true,
        "order": [[ 1, 'desc' ]],
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: {
                'action': 'searchdata'
            },
            dataSrc: ""
        },
        columns: [
            { "data": "id" },
            { "data": "date_joined" },
            { "data": "in_store.name" },
            { "data": "out_store.name" },
            { "data": "description" },
            { "data": "id" },
        ],
        columnDefs: [
            
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '';
                    // buttons += '<a href="/erp/output/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ' 
                    buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat "><i class="fas fa-search"></i></a> ';
                    
                    buttons += '<a href="/erp/movement/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat "><i class="fas fa-trash-alt"></i></a> ';
                     
                    buttons += '<a href="/erp/movement/invoice/pdf/'+row.id+'/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a> ';

                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });

    $('#example tbody')
        .on('click', 'a[rel="details"]', function () {
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var data = tblSale.row(tr.row).data();
            console.log(data);

            $('#tblDet').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                //data: data.det,
                ajax: {
                    url: window.location.pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_details_prod',
                        'id': data.id
                    },
                    dataSrc: ""
                },
                columns: [
                    { "data": "prod.name" },
                    { "data": "prod.cate.name" },
                    { "data": "amount" },
                ],
                columnDefs: [
                    
                ],
                initComplete: function (settings, json) {

                }
            });

            $('#myModelDet').modal('show');
        });
});