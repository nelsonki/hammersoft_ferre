
function toDecimal(num, decimalPlaces = 2) {
 const decimalFactor = 10 ** decimalPlaces;
 return Math.round(num * decimalFactor) / decimalFactor;
}
 


var tblProducts;
var vents = {
    items: {
        num_liquidacion:'',
        tipoFacNot:'',
        cli: '',
        date_joined: '',
        subtotal: 0.00,
        tax: 0.00,
        total: 0.00,
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
        $.each(this.items.products, function (pos, dict) {          
                dict.pos = pos;
                let a = dict.amount
                let b = dict.price_in
                console.log(a)
                console.log(b)
                let c  = a * b 
                console.log(toDecimal(c,2))
                let result = toDecimal(c,2)
                dict.subtotal = result ;
                subtotal += dict.subtotal         
            
        });
        this.items.subtotal = toDecimal(subtotal,2);
        this.items.tax = toDecimal(this.items.subtotal * tax,2);
        this.items.total = toDecimal(this.items.subtotal + this.items.tax,2);

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2) );
        $('input[name="taxcalc"]').val(this.items.tax.toFixed(2) );
        $('input[name="total"]').val(this.items.total.toFixed(2) );
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
            data: this.items.products,
            columns: [
                { "data": "id" },
                { "data": "name" },
                { "data": "stock" },
                { "data": "costBs" },
                { "data": "rate" },
                { "data": "price_in" },
                { "data": "amount" },
                { "data": "subtotal" },
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">'+data+' </span>';
                    }
                },
                
                {
                    targets: [3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return  '<input type="text" name="costBs" class="form-control form-control-sm input-sm" autocomplete="off" value="' + parseFloat(data).toFixed(2) + '">';
                    }
                },
                {
                    targets: [4],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return  '<input type="text" name="rate" class="form-control form-control-sm input-sm" autocomplete="off" value="' + parseFloat(data).toFixed(2) + '">';
                    }
                },
                {
                    targets: [5],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return  '<input type="text" name="price_in" class="form-control form-control-sm input-sm" autocomplete="off" value="' + parseFloat(data).toFixed(2)  + '">';
                    }
                },
                {
                    targets: [6],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="amount" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.amount + '">';
                    }
                },
                {
                    targets: [7],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {
 
                $(row).find('input[name="amount"]').TouchSpin({
                    min: 1,
                    max:10000,
                    step: 1
                });
              

            },
            initComplete: function (settings, json) {

            }
        });
       // console.clear();
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

        '<b>Costo Actual:</b> <span class="badge badge-warning">$' + repo.price_in + '</span>' +
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
        .val(0.16);
 

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
        .on('change ', 'input[name="costBs"]', function () {
            validarInput(this)

             var costBs = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].costBs = costBs;
           
            if(vents.items.products[tr.row].costBs !=0 && vents.items.products[tr.row].rate !=0){           
                vents.items.products[tr.row].price_in =   vents.items.products[tr.row].costBs / vents.items.products[tr.row].rate 
                vents.calculate_invoice(); 
                $('td:eq(5) input', tblProducts.row(tr.row).node()).val(vents.items.products[tr.row].price_in);
            $('td:eq(7)', tblProducts.row(tr.row).node()).html('$' +vents.items.products[tr.row].subtotal.toFixed(2));
            }

        })
        .on('change ', 'input[name="rate"]', function () {
            validarInput(this)

             var rate = parseFloat($(this).val());            
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].rate = rate;
            if(vents.items.products[tr.row].costBs !=0 && vents.items.products[tr.row].rate !=0){
                vents.items.products[tr.row].price_in =   vents.items.products[tr.row].costBs / vents.items.products[tr.row].rate   
                vents.calculate_invoice();
                $('td:eq(5) input', tblProducts.row(tr.row).node()).val(vents.items.products[tr.row].price_in);
                $('td:eq(7)', tblProducts.row(tr.row).node()).html('$' +vents.items.products[tr.row].subtotal.toFixed(2));
            }
         
        })
        .on('change ', 'input[name="price_in"]', function () {
            validarInput(this)

             var price_in = parseFloat($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();            
            vents.items.products[tr.row].price_in = price_in; 
            $('td:eq(3) input', tblProducts.row(tr.row).node()).val(0.00 );
            $('td:eq(4) input', tblProducts.row(tr.row).node()).val(0.00 );
            vents.items.products[tr.row].costBs = 0.00 
            vents.items.products[tr.row].rate = 0.00 
            vents.calculate_invoice();
            $('td:eq(7)', tblProducts.row(tr.row).node()).html('$' +vents.items.products[tr.row].subtotal.toFixed(2));
        })
        .on('change ', 'input[name="amount"]', function () {
            validarInput(this)

             var amount = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].amount = amount;
            vents.calculate_invoice();
            $('td:eq(7)', tblProducts.row(tr.row).node()).html('$' +vents.items.products[tr.row].subtotal.toFixed(2));
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
    // event submit
    $('#save').on('click', function (e) {
        e.preventDefault();
        let count=0
        if (vents.items.products.length === 0) {
            message_error('Debe al menos tener un item en su detalle de salida');
            return false;
        }
        vents.items.products.forEach(function(e, indice, array){
            if( !e.subtotal ){
                count++
                
            }
            
        });
        if(count>0){
            message_error('No puede haber campos vacios en el detalle de la salida');
            return false;
        }
        vents.items.date_joined = formatDate($('input[name="date_joined"]').val());
        vents.items.cli = $('select[name="cli"]').val();
        vents.items.tipoFacNot = $('select[name="tipoFacNot"]').val(); 
        vents.items.num_liquidacion = $('input[name="num_liquidacion"]').val();
        var parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
                alert_action('Notificación', '¿Desea imprimir la boleta de compra?', function () {
                    window.open('/erp/input/invoice/pdf/' + response.id + '/', '_blank');
                    location.href = '/erp/input/list/';
                }, function () {
                    location.href = '/erp/input/list/';
                });
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
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        data.amount = 1;
        data.price_in = 1;
        data.costBs = 0.00;
        data.rate = 0.00;
        data.subtotal = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

    vents.list();




    function validarInput(input) {
        let valor = input.value;
        if (!valor) {
           input.value = 0;
        } else {
           if (isNaN(valor)) {
             input.value = 0; 
           } else {
             input.value = valor;
           }
        }
       }
      
});