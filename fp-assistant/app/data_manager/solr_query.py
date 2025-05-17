from dataclasses import dataclass
from typing import Optional, Literal, List

@dataclass
class Query:
    base_url: str
    q: Optional[str] = None
    fq: Optional[str] = None
    fl: Optional[str] = None
    wt: Literal['csv', 'json', 'xml'] = 'json'
    rows: int = 100
    decrypt: bool = True
    start: int = 0

    def url(self) -> str:
        components = []

        if self.q:
            components.append(('q', self.q))
        else:
            components.append(('q', '*.*'))

        if self.fq:
            components.append(('fq', self.fq))

        if self.fl:
            components.append(('fl', self.fl))

        if self.wt:
            components.append(('wt', self.wt))

        if self.start:
            components.append(('start', str(self.start)))

        components.append(('rows', str(self.rows)))
        components.append(('decrypt', str(self.decrypt).lower()))

        parameters = '&'.join(['='.join(subcomponents) for subcomponents in components])
        return f'{self.base_url}?{parameters}'
