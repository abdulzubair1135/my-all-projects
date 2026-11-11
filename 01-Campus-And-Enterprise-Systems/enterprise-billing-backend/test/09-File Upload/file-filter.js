import multer from "multer";

const fileFilter = (req, file, cb) => {

    if (

        file.mimetype.startsWith("image/")

    ) {

        cb(

            null,

            true

        );

    }

    else {

        cb(

            new Error(

                "Only Images Allowed"

            )

        );

    }

};

export default fileFilter;