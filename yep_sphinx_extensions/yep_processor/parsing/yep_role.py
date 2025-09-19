from docutils import nodes
from sphinx import roles


class YEPRole(roles.ReferenceRole):
    """Override the :yep: role"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # Get YEP URI from role text.
        yep_str, _, fragment = self.target.partition("#")
        try:
            yep_num = int(yep_str)
        except ValueError:
            msg = self.inliner.reporter.error(f'invalid YEP number {self.target}', line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        yep_base = self.inliner.document.settings.yep_url.format(yep_num)
        if self.inliner.document.settings.builder == "dirhtml":
            yep_base = "../" + yep_base
        if "topic" in self.get_location():
            yep_base = "../" + yep_base
        if fragment:
            ref_uri = f"{yep_base}#{fragment}"
        else:
            ref_uri = yep_base
        if self.has_explicit_title:
            title = self.title
        else:
            title = f"YEP {yep_num}"

        return [
            nodes.reference(
                "", title,
                internal=True,
                refuri=ref_uri,
                classes=["yep"],
                _title_tuple=(yep_num, fragment)
            )
        ], []
