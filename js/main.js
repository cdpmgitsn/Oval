$(document).ready(function () {

    let site_url = window.location.origin

    toastr.options = {
        "closeButton": false,
        "debug": false,
        "newestOnTop": false,
        "progressBar": false,
        "positionClass": "toast-top-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "1000",
        "hideDuration": "1000",
        "timeOut": "7000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }

    function show_toastr(type, text) {
        toastr[type](text)
    }

    async function change_choose_currency() {
        try {
            const response = await axios.get(`${site_url}/api/trader/change-currency/`);
        } catch (error) {
            console.error(error);
        }
    }

    $('.choose-currency-select').change(function (event) {
        if ($('.currency-change-container').children('span').hasClass('not-verified')) {
            $('.currency-change-container').children('span').removeClass('not-verified').addClass('verified')
            $('.currency-change-container').children('span').children('i').removeClass('icofont-close-line').addClass('icofont-check')
            change_choose_currency()
            show_toastr('success', 'You choose your first currency!')
        }
    })

    $('.currency-change-container').click(function (event) {
        let targetElement = $(".scroll-to-currency");
        let targetPosition = targetElement.offset().top - 65;
        let containerPosition = $('#profile-card').offset().top - 65
        if (targetPosition == containerPosition) {
            $('.animate-on-currency').addClass('animate')
            setTimeout(function () {
                $('.animate-on-currency').removeClass('animate')
            }, 2000)
        } else {
            let animationDuration = 1500;
            $("html, body").animate({
                scrollTop: targetPosition
            }, animationDuration);
        }
    })

    $('.show-toastr').click(function (event) {
        let alert_type = $(this).data('toastr-type')
        let alert_text = $(this).data('toastr-text')
        show_toastr(alert_type, alert_text)
    })

    async function calculateCurrency(currency_from_id, amount, currency_to_id, result_input, container) {
        try {
            const response = await axios.get(`${site_url}/api/currency/convert/?currency_from_id=${currency_from_id}&amount=${amount}&currency_to_id=${currency_to_id}`);
            result = response.data
            $(`input[data-currency-input="${result_input}"]`).val(result.amount_format)
            $(`#${container}`).html(result.comparison)
        } catch (error) {
            console.error(error);
        }
    }

    function initCalculation(from, to, result) {
        let select1 = $(`select[data-currency-select="${from}2${to}1"]`).val()
        let amount = $(`input[data-currency-input="${from}2${to}1"]`).val()
        let select2 = $(`select[data-currency-select="${from}2${to}2"]`).val()
        if (select1 && amount && select2) {
            calculateCurrency(select1, amount, select2, `${from}2${to}2`, result)
            $(`.${from}-to-${to}-modal[data-type="error"]`).addClass('d-none')
            $(`.${from}-to-${to}-modal[data-type="success"]`).removeClass('d-none')
        } else {
            $(`.${from}-to-${to}-modal[data-type="error"]`).removeClass('d-none')
            $(`.${from}-to-${to}-modal[data-type="success"]`).addClass('d-none')
        }
    }

    $('select[data-currency-select="fiat2fiat1"]').change(function (event) {
        initCalculation('fiat', 'fiat', 'currency_result_1')
    })
    $('input[data-currency-input="fiat2fiat1"]').change(function (event) {
        initCalculation('fiat', 'fiat', 'currency_result_1')
    })
    $('select[data-currency-select="fiat2fiat2"]').change(function (event) {
        initCalculation('fiat', 'fiat', 'currency_result_1')
    })

    $('select[data-currency-select="fiat2crypto1"]').change(function (event) {
        initCalculation('fiat', 'crypto', 'currency_result_2')
    })
    $('input[data-currency-input="fiat2crypto1"]').change(function (event) {
        initCalculation('fiat', 'crypto', 'currency_result_2')
    })
    $('select[data-currency-select="fiat2crypto2"]').change(function (event) {
        initCalculation('fiat', 'crypto', 'currency_result_2')
    })

    $('select[data-currency-select="crypto2fiat1"]').change(function (event) {
        initCalculation('crypto', 'fiat', 'currency_result_3')
    })
    $('input[data-currency-input="crypto2fiat1"]').change(function (event) {
        initCalculation('crypto', 'fiat', 'currency_result_3')
    })
    $('select[data-currency-select="crypto2fiat2"]').change(function (event) {
        initCalculation('crypto', 'fiat', 'currency_result_3')
    })

    async function set_calculation_value(input, currency_from, output, currency_to, cont1, cont2, slug, event) {
        try {
            const response = await axios.get(`${site_url}/api/currency/display/?input=${input}&currency_from=${currency_from}&output=${output}&currency_to=${currency_to}`);
            result = response.data
            if (response.data.error) {
                $(`.${slug}-form`).addClass('d-none')
                show_toastr('error', response.data.error)
                event.preventDefault()
            } else {
                $(`.${slug}-form`).removeClass('d-none')
                $(cont1).html(`<b>${result.from_amount}</b> ${result.from_currency}`)
                $(cont2).html(`<b>${result.to_amount}</b> ${result.to_currency}`)
                $('input[name="exchange_id"]').val(result.exchange_id)
                $(`.${slug}-link`).html(`
                    <a href="${result.url}" class="btn btn-primary" target="_blank">
                        <i class="fa fa-file-invoice-dollar"></i>
                    </a>
                `)
            }
        } catch (error) {
            console.error(error);
        }
    }

    $('.fiat-to-fiat-modal').click(function (event) {
        let currency_from = $('select[data-currency-select="fiat2fiat1"]').val()
        let currency_amount = $('input[data-currency-input="fiat2fiat1"]').val()
        let currency_to = $('select[data-currency-select="fiat2fiat2"]').val()
        let currency_result = $('input[data-currency-input="fiat2fiat2"]').val()
        if (currency_from && currency_amount && currency_to && currency_result) {
            set_calculation_value(currency_amount, currency_from, currency_result, currency_to, `#fiat_to_fiat_currency_from_container`, `#fiat_to_fiat_currency_to_container`, 'f2f', event)
        }
    })

    $('.fiat-to-crypto-modal').click(function (event) {
        let currency_from = $('select[data-currency-select="fiat2crypto1"]').val()
        let currency_amount = $('input[data-currency-input="fiat2crypto1"]').val()
        let currency_to = $('select[data-currency-select="fiat2crypto2"]').val()
        let currency_result = $('input[data-currency-input="fiat2crypto2"]').val()
        if (currency_from && currency_amount && currency_to && currency_result) {
            set_calculation_value(currency_amount, currency_from, currency_result, currency_to, `#fiat_to_crypto_currency_from_container`, `#fiat_to_crypto_currency_to_container`, 'f2c', event)
        }
    })

    $('.crypto-to-fiat-modal').click(function (event) {
        let currency_from = $('select[data-currency-select="crypto2fiat1"]').val()
        let currency_amount = $('input[data-currency-input="crypto2fiat1"]').val()
        let currency_to = $('select[data-currency-select="crypto2fiat2"]').val()
        let currency_result = $('input[data-currency-input="crypto2fiat2"]').val()
        if (currency_from && currency_amount && currency_to && currency_result) {
            set_calculation_value(currency_amount, currency_from, currency_result, currency_to, `#crypto_to_fiat_currency_from_container`, `#crypto_to_fiat_currency_to_container`, 'c2f', event)
        }
    })

})