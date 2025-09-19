from pathlib import Path

from docutils import nodes
from docutils import transforms
from docutils import utils
from docutils.parsers.rst import roles
from docutils.parsers.rst import states


class YEPTitle(transforms.Transform):
    """Add YEP title and organise document hierarchy."""

    # needs to run before docutils.transforms.frontmatter.DocInfo and after
    # yep_processor.transforms.yep_title.YEPTitle
    default_priority = 335

    def apply(self) -> None:
        if not Path(self.document["source"]).match("yep-*"):
            return  # not a YEP file, exit early

        # Directory to hold the YEP's RFC2822 header details, to extract a title string
        yep_header_details = {}

        # Iterate through the header fields, which are the first section of the document
        desired_fields = {"YEP", "Title"}
        fields_to_remove = []
        for field in self.document[0]:
            # Hold details of the attribute's tag against its details
            row_attributes = {sub.tagname: sub.rawsource for sub in field}
            yep_header_details[row_attributes["field_name"]] = row_attributes["field_body"]

            # Store the redundant fields in the table for removal
            if row_attributes["field_name"] in desired_fields:
                fields_to_remove.append(field)

            # We only need the YEP number and title
            if yep_header_details.keys() >= desired_fields:
                break

        # Create the title string for the YEP
        yep_number = int(yep_header_details["YEP"])
        yep_title = yep_header_details["Title"]
        yep_title_string = f"YEP {yep_number} -- {yep_title}"  # double hyphen for en dash

        # Generate the title section node and its properties
        title_nodes = _line_to_nodes(yep_title_string)
        yep_title_node = nodes.section("", nodes.title("", "", *title_nodes, classes=["page-title"]), names=["yep-content"])

        # Insert the title node as the root element, move children down
        document_children = self.document.children
        self.document.children = [yep_title_node]
        yep_title_node.extend(document_children)
        self.document.note_implicit_target(yep_title_node, yep_title_node)

        # Remove the now-redundant fields
        for field in fields_to_remove:
            field.parent.remove(field)


def _line_to_nodes(text: str) -> list[nodes.Node]:
    """Parse RST string to nodes."""
    document = utils.new_document("<inline-rst>")
    document.settings.pep_references = document.settings.rfc_references = False  # patch settings
    states.RSTStateMachine(state_classes=states.state_classes, initial_state="Body").run([text], document)  # do parsing
    roles._roles.pop("", None)  # restore the "default" default role after parsing a document
    return document[0].children
