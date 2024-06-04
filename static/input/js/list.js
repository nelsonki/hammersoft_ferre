var tblSale;
var time= {
    status: '',
    date_reminder: '',
    date_pay: ''
}
$(function () {

    tblSale = $('#example').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        "ordering": true,
        "order": [[ 4, 'desc' ]],
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
            { "data": "num_liquidacion" },
            { "data": "tipoFacNot.name" },
            { "data": "cli" },
            { "data": "date_joined" },
            { "data": "date_reminder" },
            { "data": "date_pay" },

            { "data": "subtotal" },
            { "data": "tax" },
            { "data": "total" },
            { "data": "status.name" },
            { "data": "id" },
        ],
        columnDefs: [
            {
                targets: [-3, -4, -5],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return '$' + parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [5],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    fecha = new Date();
                    var strFecha = new Date(fecha.getFullYear(), fecha.getMonth(), fecha.getDate(), fecha.getHours(), fecha.getMinutes());
                    var dateFecha1 = new Date(strFecha);
                    var dateFecha2 = new Date(row.date_reminder);
                    var html = '';
                    if(dateFecha1 > dateFecha2 && row.status.id=='0') {
                        html += '<span class="text-danger"  >' + data + '</span> ';
                    }else{
                        html += data;
                    };
                    return html;
                }
            },
            {
                targets: [-2],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    var html = '';
                    if(data=='Por pagar') {
                        html += '<span class="badge badge-warning"  >' + data + '</span> ';
                    }else{
                        html += '<span class="badge badge-success">' + data + '</span> ';

                    };
                    return html;
                }
            },
            {
                targets: [-1],
                class: 'text-right',
                orderable: false,
                render: function (data, type, row) {
                    var buttons = '';
                    // buttons += '<a href="/erp/input/update/' + row.id + '/" class="btn btn-warning btn-xs btn-flat"><i class="fas fa-edit"></i></a> ' 
                    buttons += '<a rel="details" class="btn btn-success btn-xs btn-flat "><i class="fas fa-search"></i></a> ';
                    if(row.status.name =='Por pagar'){  
                        buttons += '<a rel="time" class="btn btn-warning btn-xs btn-flat "><i class="fas fa-clock"></i></a> ';
                    }
                    buttons += '<a href="/erp/input/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat "><i class="fas fa-trash-alt"></i></a> ';
                    buttons += '<a href="/erp/input/invoice/pdf/'+row.id+'/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a> ';
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
                    { "data": "costBs" },
                    { "data": "rate" },
                    { "data": "cost" },
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
        })
        .on('click', 'a[rel="time"]', function () {//aqui le damos click para que podamos colocar el timepo en que se realizara el pago de la factura
            var tr = tblSale.cell($(this).closest('td, li')).index();
            var data = tblSale.row(tr.row).data();
            console.log(data);

 
            $('#myModalTime').modal('show');

            $('#frmTime').on('submit', function (e) {
                e.preventDefault();
                var parameters = new FormData(this);
                time.date_reminder = $('input[name="date_reminder"]').val();
                time.status = $('select[name="status"]').val();

                if(time.status=='1'){
                    time.date_pay = ''

                }else{
                    time.date_pay =''
                }
                parameters.append('action', 'search_time'); 
                parameters.append('id', data.id);                
               
                parameters.append('time', JSON.stringify(time));
                submit_with_ajax(window.location.pathname, 'Notificación',
                    '¿Estas seguro de actulizar este registro?', parameters, function (response) {
                        $('#myModelTime').modal('hide');
                        location.href = '/erp/input/list/';
                    });
            });  
        });

    // formato de fecha
    function formatDate(date) { 
        var d = date.split(" ");
        var    hora = d[1];
        var    fecha = d[0];
        var    v = fecha.split("/");
        var    year = v[2];
        var    month = v[1];
        var    day = v[0];
        var    fechNueva=[year, month, day].join('-');
        return [fechNueva, hora].join(' ')
    }
        
});