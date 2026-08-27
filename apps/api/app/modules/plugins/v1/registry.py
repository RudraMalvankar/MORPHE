from typing import Dict, List

from app.modules.plugins.v1.acm import ACMPlugin
from app.modules.plugins.v1.base import BaseJournalPluginV1
from app.modules.plugins.v1.elsevier import ElsevierPlugin
from app.modules.plugins.v1.ieee import IEEEPlugin
from app.modules.plugins.v1.nature import NaturePlugin
from app.modules.plugins.v1.publishers import (
    MDPIPlugin,
    PLOSPlugin,
    TaylorFrancisPlugin,
    WileyPlugin,
)
from app.modules.plugins.v1.publishers2 import (
    BMJPlugin,
    CambridgePressPlugin,
    CellPressPlugin,
    FrontiersPlugin,
    JAMAPlugin,
    OxfordPressPlugin,
)
from app.modules.plugins.v1.publishers3 import (
    ACSPlugin,
    AMSPlugin,
    AnnualReviewsPlugin,
    APSPlugin,
    EmeraldPlugin,
    IOPPlugin,
    LancetPlugin,
    SAGEPlugin,
    ScienceAAASPlugin,
    SIAMPlugin,
)
from app.modules.plugins.v1.springer import SpringerPlugin

_registry: Dict[str, BaseJournalPluginV1] = {}


def _build_registry() -> Dict[str, BaseJournalPluginV1]:
    plugins = [
        IEEEPlugin(),
        ACMPlugin(),
        ElsevierPlugin(),
        SpringerPlugin(),
        NaturePlugin(),
        WileyPlugin(),
        TaylorFrancisPlugin(),
        MDPIPlugin(),
        PLOSPlugin(),
        OxfordPressPlugin(),
        CambridgePressPlugin(),
        FrontiersPlugin(),
        CellPressPlugin(),
        BMJPlugin(),
        JAMAPlugin(),
        ACSPlugin(),
        APSPlugin(),
        SIAMPlugin(),
        IOPPlugin(),
        AMSPlugin(),
        EmeraldPlugin(),
        SAGEPlugin(),
        AnnualReviewsPlugin(),
        LancetPlugin(),
        ScienceAAASPlugin(),
    ]
    return {p.publisher_id: p for p in plugins}


def get_plugin(publisher_key: str) -> BaseJournalPluginV1:
    if not _registry:
        _registry.update(_build_registry())
    return _registry[publisher_key]


def list_plugins() -> List[Dict[str, str]]:
    if not _registry:
        _registry.update(_build_registry())
    return [
        {
            "key": p.publisher_id,
            "name": p.publisher_name,
            "latex_class": p.latex_class,
            "citation_style": p.citation_style.in_text_format,
        }
        for p in _registry.values()
    ]
