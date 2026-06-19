/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

//
// TranslatorView.swift
//
// Main iPhone control surface for the glasses translator display.
//

import SwiftUI

struct TranslatorView: View {
  var displayViewModel: DisplayViewModel

  @State private var viewModel = TranslatorCaptionViewModel()

  var body: some View {
    ScrollView {
      VStack(spacing: 18) {
        header
        glassesCard
        liveCaptionCard
        previewCard
      }
      .padding(20)
    }
    .background(Color(.systemGroupedBackground))
    .navigationTitle("Translator")
    .navigationBarTitleDisplayMode(.inline)
    .onAppear {
      viewModel.showReady(displayViewModel: displayViewModel)
    }
  }

  private var header: some View {
    VStack(alignment: .leading, spacing: 12) {
      HStack(spacing: 12) {
        Image(systemName: "captions.bubble.fill")
          .font(.system(size: 24, weight: .semibold))
          .foregroundStyle(.white)
          .frame(width: 52, height: 52)
          .background(Color(red: 0.12, green: 0.46, blue: 0.82), in: RoundedRectangle(cornerRadius: 14))

        VStack(alignment: .leading, spacing: 4) {
          Text("Live Glasses Translator")
            .font(.title2.weight(.semibold))
          Text("Chinese speech to English captions")
            .font(.subheadline)
            .foregroundStyle(.secondary)
        }

        Spacer()
      }

      HStack(spacing: 8) {
        statusPill(
          title: displayViewModel.isConnected ? "Glasses connected" : "Glasses idle",
          color: displayViewModel.isConnected ? .green : .orange
        )
        statusPill(
          title: viewModel.isSocketConnected ? "Live backend" : "Backend off",
          color: viewModel.isSocketConnected ? .blue : .gray
        )
      }
    }
  }

  private var glassesCard: some View {
    card {
      VStack(alignment: .leading, spacing: 14) {
        sectionHeader("Glasses display", systemImage: "eyeglasses")

        HStack(spacing: 10) {
          primaryButton(title: "Show", systemImage: "rectangle.inset.filled") {
            viewModel.showReady(displayViewModel: displayViewModel)
          }

          secondaryButton(title: "Demo", systemImage: "play.fill") {
            Task { await viewModel.sendDemo(displayViewModel: displayViewModel) }
          }
        }

        if displayViewModel.isSending {
          Label("Sending to glasses", systemImage: "arrow.up.forward")
            .font(.footnote)
            .foregroundStyle(.secondary)
        }

        if let error = displayViewModel.errorMessage {
          Label(error, systemImage: "exclamationmark.triangle.fill")
            .font(.footnote)
            .foregroundStyle(.orange)
        }
      }
    }
  }

  private var liveCaptionCard: some View {
    card {
      VStack(alignment: .leading, spacing: 14) {
        sectionHeader("Live captions", systemImage: "waveform")

        TextField("ws://192.168.1.124:8000/ws/captions", text: $viewModel.serverURLString)
          .font(.system(.footnote, design: .monospaced))
          .textInputAutocapitalization(.never)
          .autocorrectionDisabled()
          .keyboardType(.URL)
          .padding(12)
          .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 10))

        HStack(spacing: 10) {
          primaryButton(
            title: viewModel.isSocketConnected ? "Disconnect" : "Connect",
            systemImage: viewModel.isSocketConnected ? "stop.fill" : "bolt.fill"
          ) {
            if viewModel.isSocketConnected {
              viewModel.disconnect()
            } else {
              viewModel.connect(displayViewModel: displayViewModel)
            }
          }

          secondaryButton(
            title: viewModel.isPaused ? "Resume" : "Pause",
            systemImage: viewModel.isPaused ? "play.fill" : "pause.fill"
          ) {
            viewModel.togglePause()
          }
        }

        Toggle("Auto-send captions to glasses", isOn: $viewModel.autoSendToGlasses)
          .font(.subheadline)

        HStack {
          Label(viewModel.statusText, systemImage: "circle.fill")
            .font(.footnote)
            .foregroundStyle(viewModel.isSocketConnected ? .blue : .secondary)
          Spacer()
          Text("\(viewModel.captionCount)")
            .font(.footnote.monospacedDigit())
            .foregroundStyle(.secondary)
        }

        if let error = viewModel.lastErrorMessage {
          Label(error, systemImage: "exclamationmark.triangle.fill")
            .font(.footnote)
            .foregroundStyle(.orange)
        }
      }
    }
  }

  private var previewCard: some View {
    card {
      VStack(alignment: .leading, spacing: 14) {
        sectionHeader("Current caption", systemImage: "text.bubble")

        if let caption = viewModel.lastCaption {
          VStack(alignment: .leading, spacing: 10) {
            Text(caption.mode.displayLabel)
              .font(.caption.weight(.semibold))
              .foregroundStyle(.secondary)

            Text(caption.translatedText)
              .font(.title3.weight(.semibold))
              .foregroundStyle(.primary)
              .frame(maxWidth: .infinity, alignment: .leading)

            if !caption.sourceText.isEmpty {
              Text(caption.sourceText)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            }
          }
          .padding(14)
          .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))

          secondaryButton(title: "Clear", systemImage: "xmark") {
            viewModel.clear(displayViewModel: displayViewModel)
          }
        } else {
          Text("No caption yet")
            .font(.subheadline)
            .foregroundStyle(.secondary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(14)
            .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 12))
        }
      }
    }
  }

  private func card<Content: View>(@ViewBuilder content: () -> Content) -> some View {
    content()
      .padding(16)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(Color(.systemBackground), in: RoundedRectangle(cornerRadius: 16))
  }

  private func sectionHeader(_ title: String, systemImage: String) -> some View {
    HStack(spacing: 8) {
      Image(systemName: systemImage)
        .foregroundStyle(Color(red: 0.10, green: 0.45, blue: 0.62))
      Text(title)
        .font(.headline)
      Spacer()
    }
  }

  private func statusPill(title: String, color: Color) -> some View {
    HStack(spacing: 6) {
      Circle()
        .fill(color)
        .frame(width: 7, height: 7)
      Text(title)
        .font(.caption.weight(.medium))
    }
    .padding(.horizontal, 10)
    .padding(.vertical, 6)
    .background(Color(.systemBackground), in: Capsule())
  }

  private func primaryButton(title: String, systemImage: String, action: @escaping () -> Void) -> some View {
    SwiftUI.Button(action: action) {
      Label(title, systemImage: systemImage)
        .font(.subheadline.weight(.semibold))
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color(red: 0.12, green: 0.36, blue: 0.86), in: RoundedRectangle(cornerRadius: 12))
    }
    .buttonStyle(.plain)
  }

  private func secondaryButton(title: String, systemImage: String, action: @escaping () -> Void) -> some View {
    SwiftUI.Button(action: action) {
      Label(title, systemImage: systemImage)
        .font(.subheadline.weight(.semibold))
        .foregroundStyle(Color(red: 0.10, green: 0.24, blue: 0.38))
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color(red: 0.86, green: 0.93, blue: 0.95), in: RoundedRectangle(cornerRadius: 12))
    }
    .buttonStyle(.plain)
  }
}
