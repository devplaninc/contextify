import type {GitHubRepository} from "@devplan/observer-api";
import {AnalysisList} from "@/components/analysis/AnalysisList.tsx";

export function RepoAnalysisList({repo}: { repo: GitHubRepository }) {
  return <AnalysisList kind="repos" keysFiler={k => k.key.startsWith(repo.fullName)}/>
}