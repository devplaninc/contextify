import {useProcessingItems} from "@/components/processing/use-processing.tsx";
import {ProcessingItemKey, ProcessingItemsFilter} from "@devplan/contextify-api";
import {useState} from "react";
import {ErrorAlert} from "../ErrorAlert";
import {Loader} from "@/components/Loader.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Button} from "@/components/ui/button.tsx";

export function ProcessingItems() {
  const [filter, setFilter] = useState<ProcessingItemsFilter>(ProcessingItemsFilter.create({}))
  const [keyFiler, setKeyFilter] = useState("")
  const {items, error, reload} = useProcessingItems(filter)
  const onApply = () => {
    const key = keyFiler.trim().length > 0 ? ProcessingItemKey.fromJSON(JSON.parse(keyFiler)) : undefined
    setFilter(v => ({...v, keys: key ? [key] : []}))
    void reload().then(() => console.log("reloaded"))
  }
  if (items === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }
  return <div className="space-y-2 border rounded-lg p-4">
    <div className="text-sm space-y-2">
      <div className="flex items-center font-semibold space-y-2 p-4 gap-4">
        Filters:
        <div className="border rounded flex gap-2 px-2 py-1 items-center">
          <div>Key:</div>
          <div><Input onChange={v => setKeyFilter(v.target.value)}/></div>
        </div>
      </div>
      <Button size="sm" onClick={onApply}>Apply</Button>
    </div>
    {items.map(i => <div key={JSON.stringify(i.key)} className="border rounded-md shadow p-2 text-sm">
      <div>{i.key?.entity?.$case} - {i.key?.entity?.value}</div>
    </div>)}
  </div>
}
