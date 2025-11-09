
{{/*
Expand the name of the chart.
*/}}
{{- define "contextify.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "contextify.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "contextify.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "contextify.labels" -}}
helm.sh/chart: {{ include "contextify.chart" . }}
{{ include "contextify.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "contextify.selectorLabels" -}}
app.kubernetes.io/name: {{ include "contextify.name" . }}
{{- end }}

{{/*
Web component labels
*/}}
{{- define "contextify.web.labels" -}}
{{ include "contextify.labels" . }}
app.kubernetes.io/component: web
{{- end }}

{{/*
Web component selector labels
*/}}
{{- define "contextify.web.selectorLabels" -}}
{{ include "contextify.selectorLabels" . }}
app.kubernetes.io/component: web
{{- end }}

{{/*
Server component labels
*/}}
{{- define "contextify.server.labels" -}}
{{ include "contextify.labels" . }}
app.kubernetes.io/component: server
{{- end }}

{{/*
Server component selector labels
*/}}
{{- define "contextify.server.selectorLabels" -}}
{{ include "contextify.selectorLabels" . }}
app.kubernetes.io/component: server
{{- end }}

{{/*
Create the name of the web service account to use
*/}}
{{- define "contextify.web.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (printf "%s-web" (include "contextify.fullname" .)) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the server service account to use
*/}}
{{- define "contextify.server.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (printf "%s-server" (include "contextify.fullname" .)) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Web deployment name
*/}}
{{- define "contextify.web.fullname" -}}
{{- printf "%s-web" (include "contextify.fullname" .) }}
{{- end }}

{{/*
Server deployment name
*/}}
{{- define "contextify.server.fullname" -}}
{{- printf "%s-server" (include "contextify.fullname" .) }}
{{- end }}

{{/*
Web service name
*/}}
{{- define "contextify.web.serviceName" -}}
{{- printf "%s-web" (include "contextify.fullname" .) }}
{{- end }}

{{/*
Server service name
*/}}
{{- define "contextify.server.serviceName" -}}
{{- printf "%s-server" (include "contextify.fullname" .) }}
{{- end }}

{{/*
Validate required image tags
*/}}
{{- define "contextify.validateImageTags" -}}
{{- if not .Values.image.web.tag }}
{{- fail "You must set image.web.tag in values.yaml; no default allowed." }}
{{- end }}
{{- if not .Values.image.server.tag }}
{{- fail "You must set image.server.tag in values.yaml; no default allowed." }}
{{- end }}
{{- end }}