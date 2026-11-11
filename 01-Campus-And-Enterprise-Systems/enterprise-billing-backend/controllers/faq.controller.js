import * as Faq from "../models/Faq.js";

export const getFaqs = async (req, res) => {

    try {

        const faqs = await Faq.getAllFaqs();

        res.json({

            success: true,

            count: faqs.length,

            data: faqs

        });

    } catch (err) {

        res.status(500).json({

            success: false,

            message: err.message

        });

    }

};

export const getFaqById = async (req, res) => {

    try {

        const faq = await Faq.getFaqById(req.params.id);

        if (!faq) {

            return res.status(404).json({

                success: false,

                message: "FAQ not found"

            });

        }

        res.json({

            success: true,

            data: faq

        });

    } catch (err) {

        res.status(500).json({

            success: false,

            message: err.message

        });

    }

};

export const createFaq = async (req, res) => {

    try {

        const result = await Faq.createFaq(req.body);

        res.status(201).json({

            success: true,

            message: "FAQ created successfully",

            id: result.insertId

        });

    } catch (err) {

        res.status(500).json({

            success: false,

            message: err.message

        });

    }

};

export const updateFaq = async (req, res) => {

    try {

        const result = await Faq.updateFaq(

            req.params.id,

            req.body

        );

        if (result.affectedRows === 0) {

            return res.status(404).json({

                success: false,

                message: "FAQ not found"

            });

        }

        res.json({

            success: true,

            message: "FAQ updated successfully"

        });

    } catch (err) {

        res.status(500).json({

            success: false,

            message: err.message

        });

    }

};

export const deleteFaq = async (req, res) => {

    try {

        const result = await Faq.deleteFaq(req.params.id);

        if (result.affectedRows === 0) {

            return res.status(404).json({

                success: false,

                message: "FAQ not found"

            });

        }

        res.json({

            success: true,

            message: "FAQ deleted successfully"

        });

    } catch (err) {

        res.status(500).json({

            success: false,

            message: err.message

        });

    }

};