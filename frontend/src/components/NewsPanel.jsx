import React from 'react'
import { ExternalLink } from 'lucide-react'

const NewsPanel = ({ newsData }) => {
  if (!newsData || !newsData.news || newsData.news.length === 0) {
    return (
      <div className="bg-surface rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Latest News</h3>
        <p className="text-muted">No news available</p>
      </div>
    )
  }

  return (
    <div className="bg-surface rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Latest News</h3>
      <div className="space-y-4">
        {newsData.news.slice(0, 10).map((article, idx) => (
          <div
            key={idx}
            className="border-b border-text-muted/10 pb-4 last:border-b-0"
          >
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-start gap-2 hover:text-primary transition"
            >
              <div className="flex-1">
                <h4 className="font-medium text-sm group-hover:text-primary transition">
                  {article.title}
                </h4>
                <p className="text-xs text-muted mt-1">
                  {article.source} •{' '}
                  {new Date(article.published_at).toLocaleDateString()}
                </p>
                {article.summary && (
                  <p className="text-xs text-muted mt-2 line-clamp-2">
                    {article.summary}
                  </p>
                )}
              </div>
              <ExternalLink size={14} className="text-muted shrink-0 mt-1" />
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

export default NewsPanel
