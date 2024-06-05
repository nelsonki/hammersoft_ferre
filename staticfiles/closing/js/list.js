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
            { "data": "date_in" },
            { "data": "date_end" },
            { "data": "cant_input" },
            { "data": "total" },
            { "data": "bolivar" },
            { "data": "peso" },
            { "data": "dolar" },
            { "data": "observation" },
            { "data": "id" },
        ],
        columnDefs: [
            {
                targets: [ -3, -6],
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
                    
                    buttons += '<a href="/erp/closing/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat "><i class="fas fa-trash-alt"></i></a> ';
                     
                    buttons += '<a href="/erp/closing/invoice/pdf/'+row.id+'/" target="_blank" class="btn btn-info btn-xs btn-flat"><i class="fas fa-file-pdf"></i></a> ';
                    buttons += '<a rel="details" class="btn btn-warning btn-xs btn-flat "><i class="fas fa-solid fa-envelope"></i></a> ';

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
        var parameters = new FormData();
        parameters.append('action', 'search_report');
          Swal.fire({
            title: 'Notificación',
            input: 'email',
            inputPlaceholder: 'Escribe el correo...',
            inputAttributes: {
                'aria-label': 'Escribe el correo...'
            },
            showCancelButton: true,
            confirmButtonText: 'Enviar',
            cancelButtonText: 'Cancelar',
            showLoaderOnConfirm: true,
            preConfirm: (message) => {
                if (!message) {
                    Swal.showValidationMessage(
                        'No puedes enviar un mensaje vacío.'
                    )
                } else {
                    parameters.append('correo', message);
                    parameters.append('misDatos', data.id);
                    console.log(parameters)
                    for(var pair of parameters.entries()) {
                        console.log(pair[0] + ': ' + pair[1]); // Mostrará 'clave1: valor1' y 'clave2: valor2' en el console.log
                       }
                    submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de enviar el reporte?', parameters, function (response) {
                        Swal.fire({
                            title: 'Notificación',
                            text: 'El reporte fue enviado al correo',
                            icon: 'success',
                            timer: 5000,
                            onClose: () => {
                             }
                        })
                    });
  
                }
            },
            allowOutsideClick: () => !Swal.isLoading()
        })
  
   
    });
         
});