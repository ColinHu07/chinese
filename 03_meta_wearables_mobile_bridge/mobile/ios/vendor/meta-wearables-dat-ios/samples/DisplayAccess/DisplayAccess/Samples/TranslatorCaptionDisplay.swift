/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

//
// TranslatorCaptionDisplay.swift
//
// Display views for the live translator prototype.
//

import Foundation
import MWDATDisplay

enum TranslationMode: String, CaseIterable, Identifiable {
  case zhToEn = "zh_to_en"
  case enToZh = "en_to_zh"

  var id: String { rawValue }

  var displayLabel: String {
    switch self {
    case .zhToEn: "中文 -> EN"
    case .enToZh: "EN -> 中文"
    }
  }
}

struct TranslatorCaption: Equatable {
  let mode: TranslationMode
  let sourceText: String
  let translatedText: String
  let isFinal: Bool
  let latencyMs: Int?
  let createdAt: Date

  static let demo = TranslatorCaption(
    mode: .zhToEn,
    sourceText: "你好，我想去火车站。",
    translatedText: "Hi, I want to go to the train station.",
    isFinal: true,
    latencyMs: 420,
    createdAt: Date()
  )
}

enum TranslatorCaptionDisplay {
  static func ready(
    serverURL: String,
    onDemo: @escaping @Sendable () -> Void
  ) -> FlexBox {
    FlexBox(direction: .column, spacing: 14) {
      FlexBox(direction: .column, spacing: 6) {
        Text("Live Translator", style: .heading)
        Text("Ready for captions", style: .body, color: .secondary)
      }
      .padding(24)
      .background(.card)

      FlexBox(direction: .column, spacing: 6) {
        Text("Phone bridge", style: .meta, color: .secondary)
        Text(shortServerLabel(serverURL), style: .body)
      }
      .padding(20)
      .background(.card)

      Button(label: "Show demo", style: .primary, iconName: .checkmark, onClick: onDemo)
    }
  }

  static func waiting(
    serverURL: String,
    onDemo: @escaping @Sendable () -> Void
  ) -> FlexBox {
    FlexBox(direction: .column, spacing: 14) {
      FlexBox(direction: .column, spacing: 6) {
        Text("Listening", style: .heading)
        Text("Waiting for live captions", style: .body, color: .secondary)
      }
      .padding(24)
      .background(.card)

      FlexBox(direction: .row, spacing: 8, alignment: .center, crossAlignment: .center, wrap: true) {
        Text("Source", style: .meta, color: .secondary)
        Text(shortServerLabel(serverURL), style: .body)
      }
      .padding(20)
      .background(.card)

      Button(label: "Demo", style: .secondary, iconName: .checkmark, onClick: onDemo)
    }
  }

  static func caption(
    _ caption: TranslatorCaption,
    onClear: @escaping @Sendable () -> Void
  ) -> FlexBox {
    FlexBox(direction: .column, spacing: 12) {
      FlexBox(direction: .row, spacing: 8, alignment: .center, crossAlignment: .center, wrap: true) {
        Text(caption.mode.displayLabel, style: .meta, color: .secondary)
        Text(caption.isFinal ? "Final" : "Live", style: .meta)
        if let latencyMs = caption.latencyMs {
          Text("\(latencyMs) ms", style: .meta, color: .secondary)
        }
      }

      FlexBox(direction: .column, spacing: 8) {
        Text(trim(caption.translatedText, limit: 180), style: .heading)
        if !caption.sourceText.isEmpty {
          Text(trim(caption.sourceText, limit: 120), style: .body, color: .secondary)
        }
      }
      .padding(24)
      .background(.card)

      FlexBox(direction: .row, spacing: 8, alignment: .center, crossAlignment: .center, wrap: true) {
        Button(label: "Clear", style: .secondary, onClick: onClear)
      }
    }
  }

  static func cleared(
    onDemo: @escaping @Sendable () -> Void
  ) -> FlexBox {
    FlexBox(direction: .column, spacing: 14) {
      FlexBox(direction: .column, spacing: 6) {
        Text("Caption cleared", style: .heading)
        Text("The next live translation will appear here.", style: .body, color: .secondary)
      }
      .padding(24)
      .background(.card)

      Button(label: "Demo", style: .primary, iconName: .checkmark, onClick: onDemo)
    }
  }

  private static func shortServerLabel(_ serverURL: String) -> String {
    guard let url = URL(string: serverURL), let host = url.host else {
      return trim(serverURL, limit: 44)
    }

    if let port = url.port {
      return "\(host):\(port)"
    }
    return host
  }

  private static func trim(_ text: String, limit: Int) -> String {
    guard text.count > limit else { return text }
    return String(text.prefix(max(limit - 1, 0))) + "..."
  }
}
