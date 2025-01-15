$(() => {
    $(".embed-video-placeholder").on("click", function () {
        let embed = $(this).data("src-embed");
        let direct = $(this).data("src-direct");
        let video =
            embed.length > 0
                ? `<iframe class="embed-video" src="${embed}" frameborder="0" allowfullscreen></iframe>`
                : `<div class="embed-video"><p>Failed to embed video. <a href="${direct}">Direct link</a></p></div>`;
        $(this).parent().append(video);
        $(this).remove();
    });

    $("#refresh-button").on("click", function () {
        fetch($(this).data("url"), {
            method: "POST",
        }).then((response) => {
            location.reload();
        });
    });
});
