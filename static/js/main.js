$(document).ready(function () {
    $('#btn-submit').hide();
    $('#export-wrap').hide();
    $('#dataTable').hide();
    $('#result').hide();
    $('#btn-export').hide();
    $('#btn-upnew').hide();
    $('#export-result').hide();

    $("#imageUpload").change(function () {
        showFileName();
        $('#btn-submit').show();
    });

    $('#btn-upnew').click(function() {
        location.reload();
    });

    $('#upload-file').submit(function (e) {
        e.preventDefault();

        var jsonData;

        $.ajax({
            type: 'POST',
            url: '/upload',
            data: new FormData(this),
            message : '',
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                console.log(data.data);
                console.log(data.message);
                alert(data.message)
                jsonData = JSON.stringify(data.data);
                displayTable(data.data);
                // $('#result').fadeIn(800);
                // $('#result').text(' Result:  ' + data.message);
                $('#upload-wrap').hide();
                $('#export-wrap').show();
                $('#btn-export').show();
                $('#btn-upnew').show();
            },
            error: function () {
                alert('Error uploading file.');
            }
        });
        $('#btn-export').click(function(e) {
            $.ajax({
                type: 'POST',
                url: '/export',
                data: JSON.stringify({ data: jsonData }),  
                contentType: 'application/json',
                success: function (response) {
                    if (response.success) {
                        console.log(response.message);
                        alert(response.message)
                        downloadJson(response.formatted_data, 'exported_data.json');
                        location.reload();
                        // $('#export-result').fadeIn(800);
                        // $('#export-result').text(response.message);
                    } else {
                        alert('Error exporting data: ' + response.error);
                    }
                },
                error: function () {
                    alert('Error exporting data.');
                }
            });
    });
});

    function displayTable(data) {
        // Create HTML table
        var tableHTML = '<table>';
        tableHTML += '<tr><th>Username</th><th>Department</th><th>License</th><th>Installed</th><th>Brand</th><th>Model</th><th>Serial</th></tr>';

        for (var i = 0; i < data.length; i++) {
            tableHTML += '<tr>';
            for (var j = 0; j < data[i].length; j++) {
                tableHTML += '<td>' + data[i][j] + '</td>';
            }
            tableHTML += '</tr>';
        }

        tableHTML += '</table>';

        // Insert table to html
        $('#dataTable').html(tableHTML);
        $('#dataTable').show();
    }

    function downloadJson(data, filename) {
        var orderedKeys = ["username", "department", "license", "Installed", "brand", "model", "serial"];
        var jsonData = data.map(item => {
            var orderedItem = {};
            orderedKeys.forEach(key => {
                orderedItem[key] = item[key];
            });
            return orderedItem;
        });

        var blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }


    function showFileName() {
    var input = document.getElementById('imageUpload');
    var label = document.getElementById('fileName');
    if (input.files.length > 0) {
        label.innerHTML = input.files[0].name;
    } else {
        label.innerHTML = 'Choose file to upload';
    }
    }

    
});