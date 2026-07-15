import type { Item } from "./types";
import Counter from "./renderers/Counter";
import Fraction from "./renderers/Fraction";
import Algebra from "./renderers/Algebra";
import BaseTen from "./renderers/BaseTen";
import NumberLine from "./renderers/NumberLine";
import ColorTile from "./renderers/ColorTile";
import Cuisenaire from "./renderers/Cuisenaire";
import FractionCircle from "./renderers/FractionCircle";
import PatternBlock from "./renderers/PatternBlock";
import LinkingCube from "./renderers/LinkingCube";
import PlaceValueDisk from "./renderers/PlaceValueDisk";
import HundredBoard from "./renderers/HundredBoard";
import XYBoard from "./renderers/XYBoard";
import Geoboard from "./renderers/Geoboard";
import Clock from "./renderers/Clock";
import Rekenrek, { Bead } from "./renderers/Rekenrek";

/** Render a piece's SVG shape centred on the local origin, with no
 *  transform or selection chrome. Shared by the board (wrapped in a
 *  positioned <g>) and the tray (rendered into a sized preview <svg>). */
export default function ItemShape({ item }: { item: Item }) {
  switch (item.kind) {
    case "counter":
      return <Counter item={item} />;
    case "fraction":
      return <Fraction item={item} />;
    case "algebra":
      return <Algebra item={item} />;
    case "baseten":
      return <BaseTen item={item} />;
    case "numberline":
      return <NumberLine item={item} />;
    case "colortile":
      return <ColorTile item={item} />;
    case "cuisenaire":
      return <Cuisenaire item={item} />;
    case "fractioncircle":
      return <FractionCircle item={item} />;
    case "patternblock":
      return <PatternBlock item={item} />;
    case "linkingcube":
      return <LinkingCube item={item} />;
    case "pvdisk":
      return <PlaceValueDisk item={item} />;
    case "hundredboard":
      return <HundredBoard item={item} />;
    case "xyboard":
      return <XYBoard item={item} />;
    case "geoboard":
      return <Geoboard item={item} />;
    case "clock":
      return <Clock item={item} />;
    case "rekenrek":
      return <Rekenrek item={item} />;
    case "bead":
      return <Bead item={item} />;
  }
}
