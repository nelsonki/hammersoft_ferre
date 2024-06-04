var tblProducts;
 var vents = {
    items: {
        store: '',
        prod: '',
        name: '',
        subtotal: 0.00,
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


        $.each(this.items.products, function (pos, dict) {
            dict.pos = pos;
            dict.subtotal = dict.amount * parseFloat(dict.pvp);
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal;
        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));

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

                $(row).find('input[name="amount"]').TouchSpin({
                    min: 1,
                    max: data.stock,
                    step: 1
                });

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
 
    // event submit
    $('#save').on('click', function (e) {
        e.preventDefault();

        if (vents.items.products.length === 0) {
            message_error('Debe al menos tener un item en su detalle de combo');
            return false;
        }
        vents.items.name = $('input[name="name"]').val();
        vents.items.store = $('select[name="store"]').val();
        vents.items.prod = $('select[name="prod"]').val();

        var parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
                     location.href = '/erp/prodcombo/list/';
                 
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
        data.amount = 1;
        data.subtotal = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });


    //BOTON PARA EL PRODUCTO COMBO
    $('select[name="prod"]').select2({
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
                    action: 'search_products2',
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
 
    }).on('select2:select', function (e) {
        var data = e.params.data;
         console.log(data.name)
    

     });


     
    vents.list();
});