import ReactGA from 'react-ga4'

/**
 * Google Analytics Event Tracking Utility
 * Use these functions to track user interactions
 */

export const trackEvent = (eventName, params = {}) => {
    try {
        ReactGA.event(eventName, params)
        console.log(`📊 Event tracked: ${eventName}`, params)
    } catch (error) {
        console.error('Error tracking event:', error)
    }
}

// Product Analysis Events
export const trackProductAnalysisStarted = (url, model) => {
    trackEvent('product_analysis_started', {
        url: url,
        model: model,
        category: 'product_analysis'
    })
}

export const trackProductAnalysisCompleted = (productName, category) => {
    trackEvent('product_analysis_completed', {
        product_name: productName,
        category: category,
        category_label: 'product_analysis'
    })
}

export const trackCompetitorAnalysisViewed = (competitorCount) => {
    trackEvent('competitor_analysis_viewed', {
        competitor_count: competitorCount,
        category: 'competitor_analysis'
    })
}

export const trackKeywordsExtracted = (keywordCount) => {
    trackEvent('keywords_extracted', {
        keyword_count: keywordCount,
        category: 'keyword_analysis'
    })
}

// SEO Optimization Events
export const trackOptimizationStarted = (optimizationType) => {
    trackEvent('optimization_started', {
        optimization_type: optimizationType,
        category: 'seo_optimization'
    })
}

export const trackOptimizationCompleted = (optimizationType, hasDraft, hasFinal) => {
    trackEvent('optimization_completed', {
        optimization_type: optimizationType,
        has_draft: hasDraft,
        has_final: hasFinal,
        category: 'seo_optimization'
    })
}

// Batch Processing Events
export const trackBatchStarted = (rowCount, optimizationType) => {
    trackEvent('batch_processing_started', {
        row_count: rowCount,
        optimization_type: optimizationType,
        category: 'batch_processing'
    })
}

export const trackBatchCompleted = (rowCount, successCount, failureCount) => {
    trackEvent('batch_processing_completed', {
        row_count: rowCount,
        success_count: successCount,
        failure_count: failureCount,
        category: 'batch_processing'
    })
}

// Chat Events
export const trackChatMessageSent = (messageLength, model) => {
    trackEvent('chat_message_sent', {
        message_length: messageLength,
        model: model,
        category: 'chat'
    })
}

export const trackChatStarted = () => {
    trackEvent('chat_started', {
        category: 'chat'
    })
}

// Settings Events
export const trackSettingsSaved = (apiKeyUpdated, modelChanged) => {
    trackEvent('settings_saved', {
        api_key_updated: apiKeyUpdated,
        model_changed: modelChanged,
        category: 'settings'
    })
}

// File Upload Events
export const trackFileUploaded = (fileType, fileSize) => {
    trackEvent('file_uploaded', {
        file_type: fileType,
        file_size: fileSize,
        category: 'file_management'
    })
}

export const trackFileExtracted = (extractedLength) => {
    trackEvent('file_extracted', {
        extracted_text_length: extractedLength,
        category: 'file_management'
    })
}

// Report Generation Events
export const trackReportGenerated = (reportType) => {
    trackEvent('report_generated', {
        report_type: reportType,
        category: 'reporting'
    })
}

// Error Tracking
export const trackError = (errorType, errorMessage) => {
    trackEvent('error_occurred', {
        error_type: errorType,
        error_message: errorMessage.substring(0, 100), // Limit message length
        category: 'errors'
    })
}

// User Engagement Events
export const trackFeatureUsed = (featureName) => {
    trackEvent('feature_used', {
        feature_name: featureName,
        category: 'engagement'
    })
}

export const trackPageScroll = (pageType) => {
    trackEvent('page_scrolled', {
        page_type: pageType,
        category: 'engagement'
    })
}
