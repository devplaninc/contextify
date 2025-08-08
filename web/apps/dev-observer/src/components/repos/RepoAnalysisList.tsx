import {GitRepository, getRepoKeyPrefix} from "@devplan/contextify-api";
import {AnalysisList} from "@/components/analysis/AnalysisList.tsx";

export function RepoAnalysisList({repo}: { repo: GitRepository }) {
  const pref = getRepoKeyPrefix(repo.provider, repo.fullName)
  return <AnalysisList kind="repos" keysFiler={k => k.key.startsWith(pref)}/>
}