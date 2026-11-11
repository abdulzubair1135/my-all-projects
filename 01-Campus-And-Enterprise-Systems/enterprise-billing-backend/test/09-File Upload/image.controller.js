class ImageController {

    async upload(req, res) {

        try {

            if (!req.file) {

                return res.status(400).json({

                    success: false,

                    message: "No Image Selected"

                });

            }

            res.status(201).json({

                success: true,

                image: req.file.filename,

                path: req.file.path

            });

        }

        catch (err) {

            res.status(500).json({

                success: false,

                message: err.message

            });

        }

    }

}

export default new ImageController();