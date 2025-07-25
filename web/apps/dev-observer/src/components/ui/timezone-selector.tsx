import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select.tsx";

export interface TimezoneSelectorProps {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

// Common timezones with their display names
const COMMON_TIMEZONES = [
  { id: "America/New_York", label: "Eastern Time (ET)" },
  { id: "America/Chicago", label: "Central Time (CT)" },
  { id: "America/Denver", label: "Mountain Time (MT)" },
  { id: "America/Los_Angeles", label: "Pacific Time (PT)" },
  { id: "America/Anchorage", label: "Alaska Time (AKT)" },
  { id: "Pacific/Honolulu", label: "Hawaii Time (HST)" },
  { id: "UTC", label: "Coordinated Universal Time (UTC)" },
  { id: "Europe/London", label: "Greenwich Mean Time (GMT)" },
  { id: "Europe/Paris", label: "Central European Time (CET)" },
  { id: "Europe/Berlin", label: "Central European Time (CET)" },
  { id: "Europe/Rome", label: "Central European Time (CET)" },
  { id: "Europe/Madrid", label: "Central European Time (CET)" },
  { id: "Europe/Amsterdam", label: "Central European Time (CET)" },
  { id: "Europe/Stockholm", label: "Central European Time (CET)" },
  { id: "Europe/Helsinki", label: "Eastern European Time (EET)" },
  { id: "Europe/Athens", label: "Eastern European Time (EET)" },
  { id: "Europe/Moscow", label: "Moscow Standard Time (MSK)" },
  { id: "Asia/Tokyo", label: "Japan Standard Time (JST)" },
  { id: "Asia/Shanghai", label: "China Standard Time (CST)" },
  { id: "Asia/Hong_Kong", label: "Hong Kong Time (HKT)" },
  { id: "Asia/Singapore", label: "Singapore Standard Time (SGT)" },
  { id: "Asia/Seoul", label: "Korea Standard Time (KST)" },
  { id: "Asia/Kolkata", label: "India Standard Time (IST)" },
  { id: "Asia/Dubai", label: "Gulf Standard Time (GST)" },
  { id: "Australia/Sydney", label: "Australian Eastern Time (AET)" },
  { id: "Australia/Melbourne", label: "Australian Eastern Time (AET)" },
  { id: "Australia/Perth", label: "Australian Western Time (AWT)" },
  { id: "Pacific/Auckland", label: "New Zealand Standard Time (NZST)" },
];

// Function to get the current user's timezone
export function getCurrentTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch (error) {
    // Fallback to UTC if detection fails
    return "UTC";
  }
}

// Function to get timezone abbreviation for display
export function getTimezoneAbbreviation(timezoneId: string): string {
  try {
    const now = new Date();
    const formatter = new Intl.DateTimeFormat('en', {
      timeZone: timezoneId,
      timeZoneName: 'short'
    });
    const parts = formatter.formatToParts(now);
    const timeZonePart = parts.find(part => part.type === 'timeZoneName');
    return timeZonePart?.value || timezoneId;
  } catch (error) {
    // Fallback to timezone ID if abbreviation detection fails
    return timezoneId;
  }
}

export function TimezoneSelector({
  value,
  onValueChange,
  placeholder = "Select timezone...",
  disabled = false,
  className
}: TimezoneSelectorProps) {
  const currentTimezone = getCurrentTimezone();
  
  // If no value is provided, use current timezone as default
  const selectedValue = value || currentTimezone;
  
  // Find the selected timezone info
  const selectedTimezoneInfo = COMMON_TIMEZONES.find(tz => tz.id === selectedValue);
  const selectedLabel = selectedTimezoneInfo?.label || selectedValue;

  return (
    <Select value={selectedValue} onValueChange={onValueChange} disabled={disabled}>
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder}>
          {selectedLabel}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {COMMON_TIMEZONES.map((timezone) => (
          <SelectItem key={timezone.id} value={timezone.id}>
            <div className="flex flex-col">
              <span className="font-medium">{timezone.label}</span>
              <span className="text-xs text-muted-foreground">{timezone.id}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}