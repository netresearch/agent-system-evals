A user reports that the CKEditor 5 image resize is lost in the frontend.

> When using the CKEditor 5 image resize feature, the resized width is stored
> correctly in the database, but it is lost during frontend rendering.
>
> Stored HTML (database) — the RTE correctly stores the resized image width:
>
> ```html
> <figure class="image image_resized" style="width:26.43%;">
>     <img src="/fileadmin/user_upload/example.jpg" width="1334" height="1000"
>          data-htmlarea-file-uid="41667">
>     <figcaption>Caption</figcaption>
> </figure>
> ```
>
> The frontend renders:
>
> ```html
> <figure class="image image_resized" style="max-width:1334px">
>     <img src="/fileadmin/_processed_/..." width="1334" height="1000">
>     <figcaption>Caption</figcaption>
> </figure>
> ```
>
> The original resize information (`style="width:26.43%"`) is lost.

Have a look and sort it out.
