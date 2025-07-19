import * as React from "react"
import {useEffect} from "react"
import {ChevronDownIcon} from "lucide-react"

import {Button} from "@/components/ui/button"
import {Calendar} from "@/components/ui/calendar"
import {Input} from "@/components/ui/input"
import {Popover, PopoverContent, PopoverTrigger,} from "@/components/ui/popover"

export interface DateTimePickerProps {
  initial?: Date
  onSelect: (date: Date) => void
}


export function DateTimePicker({onSelect, initial}: DateTimePickerProps) {
  const [open, setOpen] = React.useState(false)
  const initialDate = initial ?? new Date()
  const [date, setDate] = React.useState(initialDate)
  const formatToHHmmss = (date: Date): string => {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
  };

  const defaultTime = formatToHHmmss(initialDate)
  useEffect(() => {
      if (date) {
        onSelect(date)

      }
    }, [onSelect, date]
  )

  return (
    <div className="flex gap-4">
      <div className="flex flex-col gap-3">
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              id="date-picker"
              className="w-32 justify-between font-normal"
            >
              {date ? date.toLocaleDateString() : "Select date"}
              <ChevronDownIcon/>
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto overflow-hidden p-0" align="start">
            <Calendar
              mode="single"
              selected={date}
              captionLayout="dropdown"
              onSelect={(d) => {
                if (d) {
                  setDate(d)
                }
                setOpen(false)
              }}
            />
          </PopoverContent>
        </Popover>
      </div>
      <div className="flex flex-col gap-3">
        <Input
          type="time"
          id="time-picker"
          step="1"
          defaultValue={defaultTime}
          onChange={v => {
            const [hours, minutes, seconds] = v.target.value.split(':').map(Number)
            setDate(d => {
              const date = new Date(d.getTime())
              date.setHours(hours)
              date.setMinutes(minutes)
              date.setSeconds(seconds)
              return date
            })
          }}
          className="bg-background appearance-none [&::-webkit-calendar-picker-indicator]:hidden [&::-webkit-calendar-picker-indicator]:appearance-none"
        />
      </div>
    </div>
  )
}
