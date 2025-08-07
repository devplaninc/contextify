import {MoreHorizontal,} from "lucide-react"
import {useMemo, useState} from "react";
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar.tsx"
import {Link} from "react-router";
import type {GitRepository} from "@devplan/contextify-api";

export function NavRepositories({repositories}: { repositories: GitRepository[] }) {
  // const { isMobile } = useSidebar()
  const toShowCnt = 4
  const [showAll, setShowAll] = useState(repositories.length <= toShowCnt)
  const shown = useMemo(
    () => showAll ? repositories : repositories.slice(0, toShowCnt), [repositories, showAll])

  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Projects</SidebarGroupLabel>
      <SidebarMenu>
        {shown.map((repo) => (
          <SidebarMenuItem key={repo.name}>
            <SidebarMenuButton asChild>
              <Link to={repo.url}>
                <span>{repo.name}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
        {!showAll && <SidebarMenuItem>
            <SidebarMenuButton onClick={() => setShowAll(true)}>
                <MoreHorizontal/>
                <span>More</span>
            </SidebarMenuButton>
        </SidebarMenuItem>}
      </SidebarMenu>
    </SidebarGroup>
  )
}
