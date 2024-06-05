$(function () {
    var miTableList= $('#example').DataTable({
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
            dataSrc: "",
            
        },
        columns: [
            {"data": "id"},
            {"data": "image"},
            {"data": "store"},
            {"data": "cate.name"},
            {"data": "name"},
            {"data": "stock_general"},
            {"data": "price_in"},
            {"data": "pvp"},
            {"data": "id"},
        ],
        columnDefs: [
            {
                targets: [1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '<img src="'+row.image+'" class="img-fluid mx-auto d-block" style="width: 48px; height: 48px;">';
                }
            },
            {
                targets: [5],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    console.log(row)
                    var html = '';
                    if(data>0 && data >row.stock_min) {
                        html += '<span class="badge badge-success"  >' + data + '</span> ';
                    }else if(row.stock_min>data && data!=0){
                        html += '<span class="badge badge-warning">' + data + '</span> ';

                    }else{
                        html += '<span class="badge badge-danger">' + data + '</span> ';

                    };
                    return html;
                }
            },
            {
                targets: [2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                     var html = '';
                    $.each(row.store, function (key, value) {
                        html += '<span  class="badge badge-success">' + value.name + '</span> ';
                    });
                    return html;
                }
            },
            {
                targets: [-3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return   parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [-2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var html = '';
                    if( parseFloat(row.price_in) > parseFloat(data) ){
                        html += '<span title="El precio de costo es mayor" class="badge badge-danger"  >' + data + '</span> ';
                    }else{
                        html +=   data ;

                    }
                    return html;
                }
            },
            {
                targets: [-1],
                class: 'text-right',
                orderable: false,
                render: function (data, type, row) {
                    console.log(data)
                    var buttons='';
                    if(row.is_combo ==true) {
                     buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat "><i class="fas fa-search"></i></a>';
                    }
                    buttons += ' <a href="/erp/product/edit/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a>';

                    buttons += '<a href="/erp/product/delete/' + row.id + '/" type="button" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash-alt"></i></a>';
                    return buttons;
                }
            },
        ],
        initComplete: function (settings, json) {

        }
        
    });
    $('#example tbody')
    .on('click', 'a[rel="details"]', function () {
        var tr = miTableList.cell($(this).closest('td, li')).index();
        var data = miTableList.row(tr.row).data();
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
                    'action': 'search_details_prod_combo',
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