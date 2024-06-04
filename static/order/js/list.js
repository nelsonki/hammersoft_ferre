var tblSale;
$(function () {

    tblSale = $('#example').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
 
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
            { "data": "cli" },
            { "data": "date_joined" },
            { "data": "subtotal" },
            { "data": "tax" },
            { "data": "total" },
            { "data": "id" },
        ],
        columnDefs: [
            {
                targets: [-2, -3, -4],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '$' + parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '';
                    buttons += '<a href="/erp/order/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-solid fa-play"></i></a> ' 
                    buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat "><i class="fas fa-search"></i></a> ';
                    
                    buttons += '<a href="/erp/order/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat "><i class="fas fa-trash-alt"></i></a> ';
                     

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
                    { "data": "price" },
                    { "data": "amount" },
                    { "data": "subtotal" },
                ],
                columnDefs: [
                    {
                        targets: [-1, -3],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return '$' + parseFloat(data).toFixed(2);
                        }
                    },
                    {
                        targets: [-2],
                        class: 'text-center',
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