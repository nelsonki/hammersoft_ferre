var tblProducts;

var vents = {
    items: {
        cli: '',
        date_joined: '',
        subtotal: 0.00,
        tax: 0.00,
        total: 0.00,
        products: []
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        var tax = $('input[name="tax"]').val();
        $.each(this.items.products, function (pos, dict) {
            dict.subtotal = dict.amount * parseFloat(dict.pvp);
            subtotal += dict.subtotal;
        });
        this.items.subtotal = subtotal;
        this.items.tax = this.items.subtotal * tax;
        this.items.total = this.items.subtotal + this.items.tax;

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2));
        $('input[name="taxcalc"]').val(this.items.tax.toFixed(2));
        $('input[name="total"]').val(this.items.total.toFixed(2));
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
                { "data": "cate.name" },
                { "data": "pvp" },
                { "data": "amount" },
                { "data": "subtotal" },
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"  ><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<input type="text" name="amount" class="form-control form-control-sm input-sm" autocomplete="off" value="' + row.amount + '">';
                    }
                },
                {
                    targets: [-1],
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
                    max: 1000000000,
                    step: 1
                });

            },
            initComplete: function (settings, json) {

            }
        });
    },
};

$(function () {
    $('.select2').select2({
        theme: "bootstrap4",
        language: 'es'
    });

    $('#date_joined').datetimepicker({
        format: 'YYYY-MM-DD',
        date: moment().format("YYYY-MM-DD"),
        locale: 'es',
        //minDate: moment().format("YYYY-MM-DD")
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

    // search products

    $('input[name="search"]').autocomplete({
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
    });
    //eliminar todos los items
    $('.btnRemoveAll').on('click', function () {
        if (vents.items.products.length == 0) return false;
        submit_option('Notificación', 'Desea eliminar todos los productos del detalle?', function () {
            vents.items.products = [];
            vents.list();
        });

    });

    // event amount

    $('#tblProducts tbody')
        .on('click', 'a[rel="remove"]', function () {
             var tr = tblProducts.cell($(this).closest('td, li')).index();
            submit_option('Notificación', 'Desea eliminar el producto del detalle?', function () {
                vents.items.products.splice(tr.row, 1);
                vents.list();
            });

            
        })
        .on('change ', 'input[name="amount"]', function () {
            console.clear();
            var amount = parseInt($(this).val());
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.items.products[tr.row].amount = amount;
            vents.calculate_invoice();
            $('td:eq(5)', tblProducts.row(tr.row).node()).html('$' + vents.items.products[tr.row].subtotal.toFixed(2));
        });

        // event borrar input de busqueda
        $('.btnClearSearch').on('click', function () {
            $('input[name="search"]').val('').focus();
        });
        // event submit
        // event submit
    $('#save').on('click', function (e) {
        e.preventDefault();

        if(vents.items.products.length === 0){
            message_error('Debe al menos tener un item en su detalle de salida');
            return false;
        }

        vents.items.date_joined = $('input[name="date_joined"]').val();
        vents.items.cli = $('select[name="cli"]').val();
        var parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        submit_with_ajax(window.location.pathname, 'Notificación', '¿Estas seguro de realizar la siguiente acción?', parameters, function () {
            location.href = '/erp/output/list/';
        });
    });

    vents.list();
});