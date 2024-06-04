var tblSale;
$(function () {

    tblSale = $('#example').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        "ordering": true,
        "order": [[ 2, 'desc' ]],
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
            { "data": "store.name" },
            { "data": "observation" },
            { "data": "id" },
        ],
        columnDefs: [
        
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '';
                    buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat "><i class="fas fa-search"></i></a> ';
                    
                    buttons += '<a href="/erp/adjustment/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat "><i class="fas fa-trash-alt"></i></a> ';
                     
                    buttons += '<a href="/erp/adjustment/invoice/pdf/'+row.id+'/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a> ';

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
                    { "data": "types.name" },
                    { "data": "store1_previous" },
                    { "data": "store2_previous" },

                    { "data": "amount" },

                    { "data": "store1_next" },
                    { "data": "store2_next" },
                ],
                columnDefs: [
                     
                    {
                        targets: [-1,-2,-3,-4,-5,-6],
                        class: 'text-right',
                        render: function (data, type, row) {
                            return data;
                        }
                    },
                ],
                initComplete: function (settings, json) {

                }
            });

            $('#myModelDet').modal('show');
        });
});