"""A module for handling Microsoft Graph API scope helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from collections.abc import Iterator


# Scope Helper Literal type
ScopeHelper = Literal[
    "basic",
    "mailbox",
    "mailbox_shared",
    "mailbox_settings",
    "message_send",
    "message_send_shared",
    "message_all",
    "message_all_shared",
    "address_book",
    "address_book_shared",
    "address_book_all",
    "address_book_all_shared",
    "calendar",
    "calendar_shared",
    "calendar_all",
    "calendar_shared_all",
    "users",
    "onedrive",
    "onedrive_all",
    "sharepoint",
    "sharepoint_dl",
    "settings_all",
    "tasks",
    "tasks_all",
    "presence",
]


MSGraphScope = Literal[
    # User scopes
    "User.Read",
    "User.ReadBasic.All",
    # Mail scopes
    "Mail.Read",
    "Mail.ReadWrite",
    "Mail.Read.Shared",
    "Mail.ReadWrite.Shared",
    "Mail.Send",
    "Mail.Send.Shared",
    # Mailbox settings scopes
    "MailboxSettings.ReadWrite",
    # Contacts scopes
    "Contacts.Read",
    "Contacts.ReadWrite",
    "Contacts.Read.Shared",
    "Contacts.ReadWrite.Shared",
    # Calendar scopes
    "Calendars.Read",
    "Calendars.ReadWrite",
    "Calendars.Read.Shared",
    "Calendars.ReadWrite.Shared",
    # File scopes
    "Files.Read.All",
    "Files.ReadWrite.All",
    # SharePoint scopes
    "Sites.Read.All",
    "Sites.ReadWrite.All",
    # Tasks scopes
    "Tasks.Read",
    "Tasks.ReadWrite",
    # Presence scope
    "Presence.Read",
]


class Office365:
    """Office365 class for interacting with Microsoft Graph API."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[ScopeHelper],
        document_library_id: str,
        path: str | None = None,
    ):
        from O365 import Account, MSGraphProtocol
        from O365.drive import Drive

        self.client_id = client_id
        self.client_secret = client_secret
        self.proto = MSGraphProtocol()
        self.load_extended_metadata = False
        self.load_auth = False
        self.folder_path = path
        # helpers to atomic scopes
        ls = [self.proto.get_scopes_for(s) for sh in scopes for s in sh]
        self.account = Account((client_id, client_secret))
        if (
            not self.account.is_authenticated
            and self.account.authenticate(requested_scopes=ls) is False  # or scopes?
        ):
            msg = "Authentication Failed"
            raise RuntimeError(msg)
        self.site = self.account.sharepoint().get_site("root", "path/tosite")
        assert self.site
        self.subsites = self.site.get_subsites()
        self.lists = self.site.get_lists()
        ls = self.site.get_list_by_name("list_name")
        self.document_library_id = document_library_id
        drive = self.account.storage().get_drive(document_library_id)
        assert drive
        self.drive = drive
        if not isinstance(self.drive, Drive):
            msg = f"There isn't a Drive with id {self.document_library_id}."
            raise ValueError(msg)  # noqa: TRY004

    def lazy_load(self) -> Iterator[Document]:
        """Load documents lazily. Use this when working at a large scale.

        Yields:
            Document: A document object representing the parsed blob.
        """
        try:
            from O365.drive import Drive, Folder
        except ImportError:
            msg = "O365 package not found, please install it with `pip install o365`"
            raise ImportError(msg)  # noqa: B904

        if self.folder_path:
            target_folder = self.drive.get_item_by_path(self.folder_path)
            if not isinstance(target_folder, Folder):
                msg = f"There isn't a folder with path {self.folder_path}."
                raise ValueError(msg)
            for blob in self._load_from_folder(target_folder):
                file_id = str(blob.metadata.get("id"))
                # if self.load_auth is True:
                #     auth_identities = self.authorized_identities(file_id)
                if self.load_extended_metadata is True:
                    extended_metadata = self.get_extended_metadata(file_id)
                    extended_metadata.update({"source_full_url": target_folder.web_url})
                for parsed_blob in self._blob_parser.lazy_parse(blob):
                    if self.load_auth is True:
                        parsed_blob.metadata["authorized_identities"] = auth_identities
                    if self.load_extended_metadata is True:
                        parsed_blob.metadata.update(extended_metadata)
                    yield parsed_blob
        if self.folder_id:
            target_folder = drive.get_item(self.folder_id)
            if not isinstance(target_folder, Folder):
                msg = f"There isn't a folder with path {self.folder_path}."
                raise ValueError(msg)
            for blob in self._load_from_folder(target_folder):
                file_id = str(blob.metadata.get("id"))
                # if self.load_auth is True:
                #     auth_identities = self.authorized_identities(file_id)
                if self.load_extended_metadata is True:
                    extended_metadata = self.get_extended_metadata(file_id)
                    extended_metadata.update({"source_full_url": target_folder.web_url})
                for parsed_blob in self._blob_parser.lazy_parse(blob):
                    if self.load_auth is True:
                        parsed_blob.metadata["authorized_identities"] = auth_identities
                    if self.load_extended_metadata is True:
                        parsed_blob.metadata.update(extended_metadata)
                    yield parsed_blob
        if self.object_ids:
            for blob in self._load_from_object_ids(drive, self.object_ids):
                file_id = str(blob.metadata.get("id"))
                # if self.load_auth is True:
                #     auth_identities = self.authorized_identities(file_id)
                if self.load_extended_metadata is True:
                    extended_metadata = self.get_extended_metadata(file_id)
                for parsed_blob in self._blob_parser.lazy_parse(blob):
                    if self.load_auth is True:
                        parsed_blob.metadata["authorized_identities"] = auth_identities
                    if self.load_extended_metadata is True:
                        parsed_blob.metadata.update(extended_metadata)
                    yield parsed_blob

        if not (self.folder_path or self.folder_id or self.object_ids):
            target_folder = drive.get_root_folder()
            if not isinstance(target_folder, Folder):
                msg = "Unable to fetch root folder"
                raise ValueError(msg)
            for blob in self._load_from_folder(target_folder):
                file_id = str(blob.metadata.get("id"))
                if self.load_auth is True:
                    auth_identities = self.authorized_identities(file_id)
                if self.load_extended_metadata is True:
                    extended_metadata = self.get_extended_metadata(file_id)
                for blob_part in self._blob_parser.lazy_parse(blob):
                    blob_part.metadata.update(blob.metadata)
                    if self.load_auth is True:
                        blob_part.metadata["authorized_identities"] = auth_identities
                    if self.load_extended_metadata is True:
                        blob_part.metadata.update(extended_metadata)
                        blob_part.metadata.update({
                            "source_full_url": target_folder.web_url
                        })
                    yield blob_part


if __name__ == "__main__":
    office365 = Office365(
        client_id="your_client_id",
        client_secret="your_client_secret",
        scopes=["sharepoint"],
        document_library_id="test",
    )


# Sharepoint Lists
# Sharepoint Lists are accessible from their Sharepoint site using .get_lists() which returns a Python list of Sharepoint list objects. A known list can be accessed by providing a list_name to .get_list_by_name('list_name') which will return the requested list as a sharepointlist object.

# #Return a list of sharepoint lists
# sp_site_lists = sp_site.get_lists()

# #Return a specific list by name
# sp_list = sp_site.get_list_by_name('list_name')
# Commmon functions on a Sharepoint list include .get_list_columns(), .get_items(), .get_item_by_id(), .create_list_item(), .delete_list_item().

# Sharepoint List Items
# Accessing a list item from a Sharepoint list is done by utilizing .get_items(), or .get_item_by_id(item_id).

# #Return a list of sharepoint list Items
# sp_list_items = sp_list.get_items()

# #Return a specific sharepoint list item by its object ID
# sp_list_item = sp_list.get_item_by_id(item_id)
