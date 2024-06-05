var date_range = null;
var miCliente = null;
var date_now = moment().format("YYYY-MM-DD HH:MM");
let parameters = {
    'action': 'search_report',
    'start_date': '',
    'end_date': '',
    'correo': '',
    'client':''
};
function generate_report() {
    console.log(parameters)
      parameters = {
        'action': 'search_report',
        'start_date': '',
        'end_date': '',
        'correo': '',
        'client':''

    };

    if (date_range !== null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD HH:MM');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD HH:MM');
    }
    parameters['client'] =miCliente
 
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
         paging: false,
         info: false,
        searching: false,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-primary btn-flat btn-xs'
            },

            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-warning btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function (doc) {
                    doc.styles = {
                        header: {
                            fontSize: 18,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 13,
                            bold: true
                        },
                        quote: {
                            italics: true
                        },
                        small: {
                            fontSize: 8
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        }
                    };
                    doc.content[1].table.widths = ['20%', '20%', '15%', '15%', '15%', '15%'];
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc.content[1].layout = {};
                    doc['footer'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'left',
                                    text: ['Fecha de creación: ', { text: date_now }]
                                },
                                {
                                    alignment: 'right',
                                    text: ['página ', { text: page.toString() }, ' de ', { text: pages.toString() }]
                                }
                            ],
                            margin: 20
                        }
                    });

                }
            },

        ],
        // columns: [
        //     {"data": "id"},
        //     {"data": "name"},
        //     {"data": "desc"},
        //     {"data": "desc"},
        // ],
        columnDefs: [
            {
                targets: [-1, -2, -3],
                class: 'text-center',
                orderable: false,
                render: function (data, type, row) {
                    return parseFloat(data).toFixed(2);
                }
            },
        ],
        initComplete: function (settings, json) {

        }
    });
}

$(function () {

  



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
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });
    $('select[name="cli"]').select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_clients'
                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
    }).on('select2:select', function (e) {
        var data = e.params.data;
            miCliente = data.id
            generate_report();
        

    }).on('select2:unselecting', function (e) {
        miCliente = ''
        generate_report();
    });
   

    generate_report();
});


