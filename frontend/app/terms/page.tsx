'use client'

import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link 
        href="/" 
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-8"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Home
      </Link>

      <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
      <p className="text-gray-600 mb-8">Last updated: {new Date().toLocaleDateString()}</p>

      <div className="prose prose-lg max-w-none">
        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
          <p className="text-gray-700 mb-4">
            By accessing and using Internify ("the Service"), you accept and agree to be bound by the terms 
            and provision of this agreement. If you do not agree to abide by the above, please do not use 
            this service.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
          <p className="text-gray-700 mb-4">
            Internify provides an automated internship application platform that:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Allows users to upload and store their resumes</li>
            <li>Searches for internship opportunities using third-party APIs</li>
            <li>Generates personalized application emails using AI</li>
            <li>Sends emails on behalf of users to potential employers</li>
            <li>Maintains a history of sent applications</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Responsibilities</h2>
          <p className="text-gray-700 mb-4">You agree to:</p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Provide accurate and truthful information in your resume</li>
            <li>Review generated emails before sending</li>
            <li>Use the service only for legitimate job application purposes</li>
            <li>Not spam or misuse the email sending functionality</li>
            <li>Maintain the confidentiality of your account credentials</li>
            <li>Not use the service for any illegal or unauthorized purpose</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Content Ownership</h2>
          <p className="text-gray-700 mb-4">
            You retain all rights to the content you upload, including your resume. By using our service, 
            you grant us permission to:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Store your resume and extracted text</li>
            <li>Process your resume to generate application emails</li>
            <li>Use your data to provide and improve our services</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. AI-Generated Content</h2>
          <p className="text-gray-700 mb-4">
            Internify uses artificial intelligence to generate application emails. You acknowledge that:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>AI-generated content may contain errors or inaccuracies</li>
            <li>You are responsible for reviewing and approving all emails before sending</li>
            <li>We do not guarantee the effectiveness of AI-generated emails</li>
            <li>The final content of sent emails is your responsibility</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Third-Party Services</h2>
          <p className="text-gray-700 mb-4">
            Our service integrates with third-party platforms. We are not responsible for:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>The accuracy of job listings from external sources</li>
            <li>Email delivery issues caused by email service providers</li>
            <li>Data processing by third-party AI services</li>
            <li>Availability or reliability of third-party APIs</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Limitation of Liability</h2>
          <p className="text-gray-700 mb-4">
            Internify is provided "as is" without warranties of any kind. We are not liable for:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Job application outcomes or hiring decisions</li>
            <li>Damages resulting from use or inability to use the service</li>
            <li>Data loss or security breaches despite our best efforts</li>
            <li>Actions taken by employers based on your applications</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Service Modifications</h2>
          <p className="text-gray-700 mb-4">
            We reserve the right to:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Modify or discontinue the service at any time</li>
            <li>Change pricing or introduce new features</li>
            <li>Suspend or terminate accounts that violate these terms</li>
            <li>Update these terms with or without notice</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Account Termination</h2>
          <p className="text-gray-700 mb-4">
            We may terminate or suspend your account if you:
          </p>
          <ul className="list-disc pl-6 text-gray-700 space-y-2">
            <li>Violate these terms of service</li>
            <li>Use the service for spam or malicious purposes</li>
            <li>Provide false or misleading information</li>
            <li>Engage in behavior that harms other users or our service</li>
          </ul>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Indemnification</h2>
          <p className="text-gray-700 mb-4">
            You agree to indemnify and hold Internify harmless from any claims, damages, or expenses 
            arising from your use of the service or violation of these terms.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Governing Law</h2>
          <p className="text-gray-700 mb-4">
            These terms shall be governed by and construed in accordance with applicable laws, without 
            regard to conflict of law provisions.
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Contact Information</h2>
          <p className="text-gray-700 mb-4">
            For questions about these terms, please contact us at:
          </p>
          <p className="text-gray-700">
            Email: <a href="mailto:legal@internify.com" className="text-primary hover:underline">legal@internify.com</a>
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Acceptance</h2>
          <p className="text-gray-700 mb-4">
            By using Internify, you acknowledge that you have read, understood, and agree to be bound by 
            these Terms of Service and our Privacy Policy.
          </p>
        </section>
      </div>
    </div>
  )
}
