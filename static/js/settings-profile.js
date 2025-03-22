$(document).ready(function () {

    let site_url = window.location.origin
    const default_city_option = $('select[name="city_id"]').children()[0]
    const current_lang = $('#current_lang').data('lang')

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

    async function set_cities(country_id, url='') {
        try {
            if (url) {
                let response = await axios.get(url);
                let result = response.data
                for (item of result.results) {
                    $('select[name="city_id"]').append(`
                        <option value="${item.id}">${item['name_' + current_lang]}</option>
                    `)
                }
                if (result.next) {
                    set_cities(country_id, result.next)
                }
            } else {
                let response = await axios.get(`${site_url}/api/city/view/?type=get_by_country&country_id=${country_id}`);
                let result = response.data
                for (item of result.results) {
                    $('select[name="city_id"]').append(`
                        <option value="${item.id}">${item['name_' + current_lang]}</option>
                    `)
                }
                if (result.next) {
                    set_cities(country_id, result.next)
                }
            }
        } catch (error) {
            console.error(error);
        }
    }

    $('select[name="country_id"]').change(function (event) {
        $('select[name="city_id"]').html(default_city_option)
        let country_id = $(this).val()
        if (country_id != '') {
            set_cities(country_id)
        }
    })

    $('#copyButton').click(function (event) {
        let text = $(this).data('text')
        navigator.clipboard.writeText(text)
        .then(() => {
            // Success message
            toastr["success"]("Text copied to clipboard");
        })
        .catch(err => {
            // Error message
            console.error('Could not copy text: ', err);
        });
    })

})