var tblProducts;
var vents = {
    items: {
        in_store: '',
        out_store: '',
        date_joined: '',
        description:'',
        products: []
    },
    get_ids: function () {
        var ids = [];
        $.each(this.items.products, function (key, value) {
            ids.push(value.id);
        });
        return ids;
    },

    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
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
                { "data": "amount" },
            ],
            columnDefs: [
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">'+data+' </span>';
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                 
                {
                    targets: [-1],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="amount" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.amount + '">';
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
    $('select[name="out_store"]').select2({
        theme: "bootstrap4",
        language: 'es',
     }).on('select2:select', function (e) {
        if ($('select[name="in_store"]').val() =! $('select[name="out_store"]').val()) return false;
        alert_action('Notificación', 'No se pueden enviar productos al mismo almacen', function () {
            vents.items.in_store = '';
            vents.items.out_store = '';
            $('select[name="in_store"]').val('')
            $('select[name="out_store"]').val('')
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
        .on('change ', 'input[name="amount"]', function () {
            console.clear();
            var amount = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].amount = amount;
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

        if (vents.items.products.length === 0) {
            message_error('Debe al menos tener un item en su detalle de salida');
            return false;
        }
        vents.items.date_joined = formatDate($('input[name="date_joined"]').val());
        vents.items.cli = $('select[name="cli"]').val();
        vents.items.in_store = $('select[name="in_store"]').val();
        vents.items.out_store = $('select[name="out_store"]').val();
        vents.items.description = $('input[name="description"]').val();

        var parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        submit_with_ajax(window.location.pathname, 'Notificación',
            '¿Estas seguro de realizar la siguiente acción?', parameters, function (response) {
                alert_action('Notificación', '¿Desea imprimir el movimiento?', function () {
                    window.open('/erp/movement/invoice/pdf/' + response.id + '/', '_blank');
                    location.href = '/erp/movement/list/';
                }, function () {
                    location.href = '/erp/movement/list/';
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
                    vaStore: $('select[name="in_store"]').val()

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
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

    vents.list();
});