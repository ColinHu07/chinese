/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 */

//
// LocalNetworkPermissionProbe.swift
//
// Starts a short Bonjour browse so iOS presents the Local Network permission
// prompt before the app opens LAN WebSocket connections to the Mac.
//

import Foundation
import Network

final class LocalNetworkPermissionProbe {
  static let shared = LocalNetworkPermissionProbe()

  private let queue = DispatchQueue(label: "com.meta.displayaccess.local-network-probe")
  private var browser: NWBrowser?

  private init() {}

  func requestIfNeeded(completion: @escaping @Sendable () -> Void) {
    let parameters = NWParameters()
    parameters.includePeerToPeer = true

    let browser = NWBrowser(for: .bonjour(type: "_http._tcp", domain: nil), using: parameters)
    self.browser = browser

    let finishOnce = FinishOnce {
      browser.cancel()
      self.browser = nil
      DispatchQueue.main.async {
        completion()
      }
    }

    browser.stateUpdateHandler = { state in
      switch state {
      case .ready, .failed, .cancelled:
        finishOnce.finish()
      default:
        break
      }
    }

    browser.start(queue: queue)
    queue.asyncAfter(deadline: .now() + 1.0) {
      finishOnce.finish()
    }
  }
}

private final class FinishOnce {
  private let lock = NSLock()
  private var didFinish = false
  private let action: () -> Void

  init(_ action: @escaping () -> Void) {
    self.action = action
  }

  func finish() {
    lock.lock()
    if didFinish {
      lock.unlock()
      return
    }
    didFinish = true
    lock.unlock()
    action()
  }
}
