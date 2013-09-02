Dropzone.options.mydropzone = {
    previewTemplate : '<div class="preview file-preview">\
    <div class="dz-details">\
        <b class="dz-filename"><span data-dz-name></span></b>\
        <b class="dz-size" data-dz-size></b>\
    </div>\
    <div class="dz-progress"><span class="dz-upload" data-dz-uploadprogress></span></div>\
    <div class="dz-error-message"><span data-dz-errormessage></span></div>\
    </div>',
    init: function() {
        this.on("complete", function(file) { console.log("Upload complete"); });
    }
};


$(document).ready(function() {
    oTable = $('#datatable').dataTable( {
        "bProcessing": true,
        "sAjaxDataProp": '',
        "sAjaxSource": '/getFiles',
    } );

    $("#datatable tbody").click(function(event){
            $(oTable.fnSettings().aoData).each(function (){
                $(this.nTr).removeClass('row_selected');
            });
            $(event.target.parentNode).addClass('row_selected');

            var id = oTable.fnGetData(event.target.parentNode)[0];
            $.ajax({
              url: "/getMatches/"+id,
            }).done(function(matches) {
                content = "";
                matches = JSON.parse(matches);
                for (var i in matches) {
                  match = matches[i];
                  content += "Match: <a href='/getRule/"+match['rule_id']+"'>"+match['description']+"</a><br>"
                }
                if (content == "") {
                    content = "No matches found";
                }
                $("#matchData").html(content);
            });
    });
} );