'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link 
        href="/" 
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </Link>

      <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
      <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>

      <div className="prose prose-lg max-w-none">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
          <p className="text-gray-700 mb-4">
            Welcome to Internify. We respect your privacy and are committed to protecting your personal data. 
            This privacy policy will inform you about how we look after your personal data when you visit our 
            platform and tell you about your privacy rights and how the law protects you.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Data We Collect</h2>
          <p className="text-gray-700 mb-4">We collect and process the following information:</p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li><strong>Account Information:</strong> Email address, name, and authentication details</li>
            <li><strong>Resume Data:</strong> PDF files and extracted text content from your resume</li>
            <li><strong>Job Search History:</strong> Search queries and selected job postings</li>
            <li><strong>Email Data:</strong> Generated emails and their content</li>
            <li><strong>Usage Data:</strong> How you interact with our platform</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Data</h2>
          <p className="text-gray-700 mb-4">We use your data to:</p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Provide and maintain our service</li>
            <li>Generate personalized application emails using AI</li>
            <li>Search for relevant internship opportunities</li>
            <li>Generate personalized emails for your applications</li>
            <li>Improve and optimize our platform</li>
            <li>Communicate with you about your account</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Data Security</h2>
          <p className="text-gray-700 mb-4">
            We implement appropriate security measures to protect your personal information. Your data is 
            stored securely using industry-standard encryption. We use Supabase for secure data storage 
            and authentication.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Third-Party Services</h2>
          <p className="text-gray-700 mb-4">We use the following third-party services:</p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li><strong>Supabase:</strong> Database, authentication, and file storage</li>
            <li><strong>Google Gemini AI:</strong> Email generation</li>
            <li><strong>SerpAPI:</strong> Job search functionality</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Retention</h2>
          <p className="text-gray-700 mb-4">
            We retain your personal data for as long as your account is active or as needed to provide you 
            services. You can delete your data at any time by deleting your resume and account information 
            from the dashboard.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Your Rights</h2>
          <p className="text-gray-700 mb-4">You have the right to:</p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Access your personal data</li>
            <li>Correct inaccurate data</li>
            <li>Delete your data</li>
            <li>Export your data</li>
            <li>Withdraw consent at any time</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Cookies</h2>
          <p className="text-gray-700 mb-4">
            We use essential cookies for authentication and session management. We do not use tracking 
            or advertising cookies.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Changes to This Policy</h2>
          <p className="text-gray-700 mb-4">
            We may update this privacy policy from time to time. We will notify you of any changes by 
            posting the new policy on this page and updating the &ldquo;Last updated&rdquo; date.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Contact Us</h2>
          <p className="text-gray-700 mb-4">
            If you have any questions about this privacy policy or our practices, please contact us at:
          </p>
          <p className="text-gray-700">
            Email: <a href="mailto:privacy@internify.com" className="text-primary hover:underline">privacy@internify.com</a>
          </p>
        </section>
      </div>
    </div>
  )
}
