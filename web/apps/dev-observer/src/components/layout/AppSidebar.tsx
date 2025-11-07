import * as React from "react"
import {Globe, IdCard, ScanSearch, ShieldUser, SquareTerminal} from "lucide-react"

import {NavSecondary} from "@/components/nav-secondary.tsx"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar.tsx"
import {NavMain} from "@/components/layout/NavMain.tsx";
import {Link} from "react-router";
import {processingPath} from "@/paths.tsx";

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Repositories",
      url: "/repositories",
      icon: SquareTerminal,
      isActive: true,
    },
    {
      title: "Websites",
      url: "/websites",
      icon: Globe,
    },
    {
      title: "Repo Tokens",
      url: "/repo_tokens",
      icon: IdCard,
    },
    {
      title: "Processing",
      url: processingPath(),
      icon: ScanSearch,
    },
    {
      title: "Admin",
      url: "",
      icon: ShieldUser,
      items: [
        {
          title: "Config",
          url: "/admin/config-editor",
        },
        {
          title: "Actions",
          url: "/admin/actions",
        }
      ],
    },
  ],
  navSecondary: [
    // {
    //   title: "Support",
    //   url: "#",
    //   icon: LifeBuoy,
    // },
    // {
    //   title: "Feedback",
    //   url: "#",
    //   icon: Send,
    // },
  ],
}

export function AppSidebar({...props}: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar
      className="top-(--header-height) h-[calc(100svh-var(--header-height))]!"
      {...props}
    >
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link to="/">
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">Dev Observer</span>
                  {/*<span className="truncate text-xs">Enterprise</span>*/}
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain}/>
        <NavSecondary items={data.navSecondary} className="mt-auto"/>
      </SidebarContent>
    </Sidebar>
  )
}
