import * as Contact from "../models/Contact.js";

// Get All Contacts
export const getContacts = async (req, res) => {

    try {

        const contacts = await Contact.getAllContacts();

        return res.status(200).json({
            success: true,
            count: contacts.length,
            data: contacts
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// Get Contact
export const getContactById = async (req, res) => {

    try {

        const contact = await Contact.getContact(req.params.id);

        if (!contact) {

            return res.status(404).json({
                success: false,
                message: "Contact not found"
            });

        }

        return res.status(200).json({
            success: true,
            data: contact
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// Create Contact
export const createContact = async (req, res) => {

    try {

        const result = await Contact.createContact(req.body);

        return res.status(201).json({
            success: true,
            message: "Contact created successfully",
            id: result.insertId
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }

};

// Delete Contact
export const deleteContact = async (req, res) => {

    try {

        const result = await Contact.deleteContact(req.params.id);

        if (result.affectedRows === 0) {

            return res.status(404).json({
                success: false,
                message: "Contact not found"
            });

        }

        return res.status(200).json({
            success: true,
            message: "Contact deleted successfully"
        });

    } catch (err) {

        return res.status(500).json({
            success: false,
            message: err.message
        });

    }

};