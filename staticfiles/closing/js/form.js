var date_range = null;
var miCliente = null;
var date_now = moment().format("YYYY-MM-DD HH:MM");
var parameters = {
    'action': 'search_report',
        'data_in': '',
        'data_end': '',
};
var misFacturas=[]
function toDecimal(num, decimalPlaces = 2) {
    const decimalFactor = 10 ** decimalPlaces;
    return Math.round(num * decimalFactor) / decimalFactor;
   }
      
 
function generate_report() {
    misFacturas=[]
    parameters = {
        'action': 'search_report',
        'data_in': '',
        'data_end': '',
    };


    if (date_range !== null) {
        parameters['data_in'] = date_range.startDate.format('YYYY-MM-DD HH:MM');
        parameters['data_end'] = date_range.endDate.format('YYYY-MM-DD HH:MM');
    }else{
        parameters['data_in'] = date_now;
        parameters['data_end'] = date_now;
      }
 
    $('#example').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: window.location.pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        "ordering": true,
        "order": [[ 1, 'desc' ]],
         paging: true,
         info: false,
         searching: false,

        columns: [
            { "data": "id" },
            { "data": "date_joined" },
            { "data": "cli" },
            { "data": "subtotal" },
        ],
        columnDefs: [
           
            {
                targets: [-1],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return parseFloat(data).toFixed(2);
                }
            },
        ],
        rowCallback(row, data, displayNum, displayIndex, dataIndex) {
        var total = 0.00;
       
         misFacturas.push(data)
         console.log(misFacturas)

         $.each(misFacturas, function (pos, dict) {  
            total += toDecimal(dict.total,2)        
         
        });
        $('input[name="total"]').val(toDecimal(total,2).toFixed(2));
        },
        initComplete: function (settings, json) {

        }
    })
     
}

$(function () {
    generate_report();

  



    $('input[name="date_range"]').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD HH:MM',
            applyLabel: '<i class="fas fa-chart-pie"></i> Aplicar',
            cancelLabel: '<i class="fas fa-times"></i> Cancelar',
        },
        timePicker: true,
        timePickerIncrement: 15,
        timePicker24Hour: true,
        timePickerSeconds: false,
    }).on('apply.daterangepicker', function (ev, picker) {
         date_range = picker;
        generate_report();
    }).on('cancel.daterangepicker', function (ev, picker) {
        $(this).data('daterangepicker').setStartDate(date_now);
        $(this).data('daterangepicker').setEndDate(date_now);
        date_range = picker;
        generate_report();
    });

 // event submit
 $('#save').on('click', function (e) {
    e.preventDefault();
     
    if (misFacturas.length == 0) {
        message_error('Debe al menos tener un item en su detalle de cierre de salidas');
        return false;
    }

    var parameters = new FormData();
    parameters.append('action', $('input[name="action"]').val());
    parameters.append('observation', $('input[name="observation"]').val());
    parameters.append('dolar', $('input[name="dolar"]').val());
    parameters.append('peso', $('input[name="peso"]').val());
    parameters.append('bolivar', $('input[name="bolivar"]').val());
    parameters.append('total', $('input[name="total"]').val());
    if (date_range !== null) {
        parameters.append('data_in', date_range.startDate.format('YYYY-MM-DD HH:MM'));
        parameters.append('data_end', date_range.endDate.format('YYYY-MM-DD HH:MM'));
    }else{
        parameters.append('data_in', date_now);
        parameters.append('data_end', date_now);
    }
    parameters.append('misFacturas', JSON.stringify(misFacturas));//esto se hace para que el vector pueda ser recibido como corresponde en la view
    console.log(misFacturas)
     submit_with_ajax(window.location.pathname, 'Notificación',
        '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
           
                location.href = '/erp/closing/list/';
            
        });
});
   

});


