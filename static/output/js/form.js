var tblProducts;
function replaceCommaWithDot(str) {
    return str.replace(/,/g, '.');
   }
var vents = {
    items: {
        store: '',
        cli: '',
        date_joined: '',
        subtotal: 0.00,
        tax: 0.00,
        total: 0.00,
        pesos:0.00,
        bolivares:0.00,
        products: []
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var tax = $('input[name="tax"]').val();
        var myPesos = $('input[name="pesos"]').val();
        var myBolivares = $('input[name="bolivares"]').val();

        var p = parseFloat(replaceCommaWithDot(myPesos));
        var b = parseFloat(replaceCommaWithDot(myBolivares));

        $.each(this.items.products, function (pos, dict) {
            dict.pos = pos;
            dict.subtotal = dict.amount * parseFloat(dict.pvp);
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal;
        this.items.tax = this.items.subtotal * tax;
        this.items.total = this.items.subtotal + this.items.tax; 
        this.items.pesos = this.items.total * p 
        this.items.bolivares = this.items.total * b

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="taxcalc"]').val(this.items.tax.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
        $('input[name="peso"]').val(this.items.pesos.toFixed(2));
        $('input[name="bolivar"]').val(this.items.bolivares.toFixed(2));

    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () { 
        this.calculate_invoice();
        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            info: false,

            data: this.items.products,
            columns: [
                { "data": "id" },
                { "data": "name" },
                { "data": "stock" },
                { "data": "typepvp" },
                { "data": "pvp" },
                { "data": "amount" },
                { "data": "subtotal" },
            ],
            columnDefs: [
                {//eliminar
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {//stock del producto
                    targets: [2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">'+data+' </span>';
                    }
                },
                {//tipo de pvp
                    targets: [3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
 
                        return "<select name='typepvp' class='form-control form-control-sm input-sm' ><option value='"+row.pvp+"' {0}>PVP</option><option value='"+row.pvp2+"' {1}>PVP opcional</option><option value='"+row.pvp3+"' {2}>PVP combo</option></select>"
                    }
                },
                {
                    targets: [4],
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
                        return '<input type="text" name="amount" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.amount + '">';
                    }
                },
                {
                    targets: [6],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {
                if(data.is_combo==0){
                    $(row).find('input[name="amount"]').TouchSpin({
                        min: 1,
                        max: data.stock,
                        step: 1
                    });
                }else{
                    $(row).find('input[name="amount"]').TouchSpin({
                        min: 1,
                        max: 1000,
                        step: 1
                    });
                }
            },
            initComplete: function (settings, json) {

            }
        });
        console.clear();
        console.log(this.items);
        console.log(this.get_ids());

    },
};

function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    var option = $(
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        '<img src="' + repo.image + '" class="img-fluid img-thumbnail d-block mx-auto rounded">' +
        '</div>' +
        '<div class="col-lg-11 text-left shadow-sm">' +
        //'<br>' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b> ' + repo.name + '<br>' +
        '<b>Categoría:</b> ' + repo.cate.name + '<br>' +
        '<b>Stock:</b> ' + repo.stock + '<br>' +

        '<b>PVP:</b> <span class="badge badge-warning">$' + repo.pvp + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}

$(function () {
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    

    $("input[name='tax']").TouchSpin({
        min: 0,
        max: 100,
        step: 0.01,
        decimals: 2,
        boostat: 5,
        maxboostedstep: 10,
        postfix: '%'
    }).on('change', function () {
        vents.calculate_invoice();
    })
        .val(0.00);
 

    // search clients

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
    });

    $('.btnAddClient').on('click', function () {
        $('#myModalClient').modal('show');
    });

    $('#myModalClient').on('hidden.bs.modal', function (e) {
        $('#frmClient').trigger('reset');
    })

    $('#frmClient').on('submit', function (e) {
        e.preventDefault();
        var parameters = new FormData(this);
        parameters.append('action', 'create_client');
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de crear al siguiente cliente?', parameters, function (response) {
                var newOption = new Option(response.full_name, response.id, false, true)
                $('select[name="cli"]').append(newOption).trigger('change')
                $('#myModalClient').modal('hide');
            });
    });

    // search products

    /*$('input[name="search"]').autocomplete({
        source: function (request, response) {
            $.ajax({
                url: window.location.pathname,
                type: 'POST',
                data: {
                    'action': 'search_products',
                    'term': request.term
                },
                dataType: 'json',
            }).done(function (data) {
                response(data);
            }).fail(function (jqXHR, textStatus, errorThrown) {
                //alert(textStatus + ': ' + errorThrown);
            }).always(function (data) {

            });
        },
        delay: 500,
        minLength: 1,
        select: function (event, ui) {
            event.preventDefault();
            console.clear();
            ui.item.amount = 1;
            ui.item.subtotal = 0.00;
            console.log(vents.items);
            vents.add(ui.item);
            $(this).val('');
        }
    });*/

    //eliminar todos los items
    $('.btnRemoveAll').on('click', function () {
        if (vents.items.products.length == 0) return false;
        alert_action('Notificación', 'Desea eliminar todos los productos del detalle?', function () {
            vents.items.products = [];
            vents.list();
        }, function () {

        });

    });
    //eliminar todos los items
    $('select[name="store"]').select2({
        theme: "bootstrap4",
        language: 'es',
     }).on('select2:select', function (e) {
        if (vents.items.products.length == 0) return false;
        alert_action('Notificación', 'Desea cambiar de almacen, perdera los productos agregados al detalle?', function () {
            vents.items.products = [];
            vents.list();
        }, function () {

        });
    });;

    // event amount

    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            alert_action('Notificación', 'Desea eliminar el producto del detalle?',
                function () {
                    vents.items.products.splice(tr.row, 1);
                    vents.list();
                }, function () {

                });

        })
        .on('change ', 'select[name="typepvp"]', function () {
            console.clear();
            var tr = tblProducts.cell($(this).closest('td, li')).index();

            var tipoSeleccionado = parseFloat($(this).val());

           if(tipoSeleccionado){
            vents.items.products[tr.row].pvp = tipoSeleccionado;
            vents.calculate_invoice();
            $('td:eq(4)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].pvp.toFixed(2));
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));

           }
           
          
           
        })
        .on('change ', 'input[name="amount"]', function () {
            
            console.clear();
            var amount = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].amount = amount;
            vents.calculate_invoice();
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));
        });

    // event borrar input de busqueda
    $('.btnClearSearch').on('click', function () {
        $('input[name="search"]').val('').focus();
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
    function validarCantidad(data, callback) {
        // Validamos si se envía la información correcta
        if (data === null || data === undefined) {
            console.error('No se envió la información correcta');
            return;
        }
        // Realizamos la solicitud ajax
        $.ajax({
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: {
                'action': 'validateCombo',
                'idsProd': JSON.stringify(data),
            },
            dataType: 'json',
        }).done(function(respuesta, textStatus, jqXHR) {
                // Si la solicitud fue exitosa, procesamos la respuesta aquí
                console.log(respuesta)
                if(respuesta.error){
                    message_error(respuesta.error);
                    callback(false); // Agregar esta línea
                }else{
                    callback(true); // Agregar esta línea
                }

            })
             
    }
    // event submit
    $('#save').on('click', function (e) {
        e.preventDefault();
        if (vents.items.products.length === 0) {
            message_error('Debe al menos tener un item en su detalle de salida');
            return false;
        }
        validarCantidad(vents.items.products, function(validar) {
            if(validar){
    vents.items.date_joined = formatDate($('input[name="date_joined"]').val());
                    vents.items.cli = $('select[name="cli"]').val();
                    vents.items.store = $('select[name="store"]').val();
                    var parameters = new FormData();
                    parameters.append('action', $('input[name="action"]').val());
                    parameters.append('vents', JSON.stringify(vents.items));
                    submit_with_ajax(window.location.pathname, 'Notificación',
                        '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
                            alert_action('Notificación', '¿Desea imprimir la boleta de venta?', function () {
                                window.open('/erp/output/invoice/pdf/' + response.id + '/', '_blank');
                                location.href = '/erp/output/list/';
                            }, function () {
                                location.href = '/erp/output/list/';
                            });
                        });
            }
            console.log(validar);
        });

      
    });
    //BOTON PARA BUSCAR LOS PRODUCTOS

    $('select[name="search"]').select2({
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
                    action: 'search_products',
                    ids: JSON.stringify(vents.get_ids()),
                    vaStore: $('select[name="store"]').val()
                }
                return queryParameters;
            },
            processResults: function (data) {
                console.log(data)               
                    return {                    
                    results: data
                };              
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1,
        templateResult: formatRepo,
    }).on('select2:select', function (e) {  
        var data = e.params.data;
        console.log(data)
        if( parseFloat(data.price_in) > parseFloat(data.pvp)){
            message_error('El costo del producto es mayor al PVP');
            $(this).val('').trigger('change.select2');
            return false;
        }else if( parseInt(data.stock) <=  0 && data.is_combo==false){
            message_error('El Stock del producto es menor o igual a 0');
            $(this).val('').trigger('change.select2');
            return false;
        }else{
             data.amount = 1;
            data.subtotal = 0.00;
            vents.add(data);
        $(this).val('').trigger('change.select2');
        }       
    });


     
    vents.list();



 

 
});