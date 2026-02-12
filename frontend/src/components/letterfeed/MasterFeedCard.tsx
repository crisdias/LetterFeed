"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Rss, ExternalLink, FileText } from "lucide-react"
import { getMasterFeedUrl, getOpmlUrl } from "@/lib/api"
import { Badge } from "@/components/ui/badge"

export function MasterFeedCard() {
  const feedUrl = getMasterFeedUrl()
  const opmlUrl = getOpmlUrl()

  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <Rss className="w-5 h-5 text-orange-500" />
          Master Feed
          <Badge variant="secondary" className="ml-2">
            <FileText className="w-3 h-3 mr-1" />
            <a
              href={opmlUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              OPML
            </a>
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          This feed contains all entries from all your newsletters in one place.
        </p>
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">RSS Feed URL</h4>
          <div className="flex items-center gap-2">
            <a
              href={feedUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              <ExternalLink className="w-3 h-3" />
              {feedUrl}
            </a>
          </div>
        </div>
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">OPML File (Individual Feeds)</h4>
          <div className="flex items-center gap-2">
            <a
              href={opmlUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              <ExternalLink className="w-3 h-3" />
              {opmlUrl}
            </a>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Import this file into your RSS reader to subscribe to each newsletter as a separate feed.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
