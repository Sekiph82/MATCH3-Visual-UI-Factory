// Real LFXV1 and Engine M3P1 boundary source tests; no live replay claims.
using System;
using System.Security.Cryptography;
using System.Text;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UI;
using Match3.VisualFactory.Editor;

namespace Match3.VisualFactory.Tests
{
    public sealed class VufCrossFactoryContractEditModeTests
    {
        private static readonly byte[] Canonical =
            Encoding.UTF8.GetBytes("{\"testOnly\":\"real LFX must provide bytes\"}");

        private static string Sha(byte[] data)
        {
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(data))
                    .Replace("-", "").ToLowerInvariant();
        }

        private static VufCrossFactoryContractWindow.Level Source()
        {
            return new VufCrossFactoryContractWindow.Level {
                schemaVersion = 1,
                stage = "LFXV1_VALIDATED_DRAFT_NOT_ENGINE_REPLAY",
                gameProfileId = "Coral_Rescue",
                levelId = "level.prototype",
                width = 2, height = 2, layers = 1, moveBudget = 17,
                seed = 731,
                sourceDraftSha256 = Sha(Canonical),
                sourceLevelFactoryGitSha = "UNPINNED",
                cells = new [] {
                    new VufCrossFactoryContractWindow.Cell {
                        row = 0, column = 0, layer = 0, active = true,
                        contentId = "gem.猫"
                    },
                    new VufCrossFactoryContractWindow.Cell {
                        row = 0, column = 1, layer = 0, active = true,
                        contentId = "gem.\"quoted\""
                    },
                    new VufCrossFactoryContractWindow.Cell {
                        row = 1, column = 0, layer = 0, active = false,
                    },
                    new VufCrossFactoryContractWindow.Cell {
                        row = 1, column = 1, layer = 0, active = true,
                        contentId = "gem.green"
                    },
                },
                goals = new [] {
                    new VufCrossFactoryContractWindow.Goal {
                        goalId = "goal.primary", targetId = "sample.score",
                        targetCount = 321
                    }
                }
            };
        }

        private static VufCrossFactoryContractWindow.Level Parse() =>
            VufCrossFactoryContractWindow.ParseLevel(
                JsonUtility.ToJson(Source()), Canonical);

        private static byte[] Wire(string rows, int count)
        {
            string body = "M3P1\nCoral_Rescue\n" + count + "\n" + rows;
            return Encoding.UTF8.GetBytes(body + Sha(Encoding.UTF8.GetBytes(body)));
        }

        [Test]
        public void GenuineLfxCompatibleSourceHasExactCoordinatesAndNoGameRights()
        {
            var level = Parse();
            Assert.That(level.cells.Length, Is.EqualTo(4));
            Assert.That(level.cells[0].contentId, Is.EqualTo("gem.猫"));
            Assert.That(level.goals[0].targetCount, Is.EqualTo(321));
            Assert.That(level.releaseAllowed, Is.False);
            Assert.That(level.actualSdkWinVerified, Is.False);
            Assert.That(level.sourceDraftSha256, Is.EqualTo(Sha(Canonical)));
        }

        [Test]
        public void SourceShaCorruptionOrFakeEngineApprovalRejects()
        {
            var bad = Source();
            bad.engineM24ReleaseAccepted = true;
            Assert.Throws<ArgumentException>(() =>
                VufCrossFactoryContractWindow.ParseLevel(
                    JsonUtility.ToJson(bad),Canonical));
            bad = Source();
            bad.sourceDraftSha256 = new string('a',64);
            Assert.Throws<ArgumentException>(() =>
                VufCrossFactoryContractWindow.ParseLevel(
                    JsonUtility.ToJson(bad),Canonical));
        }

        [Test]
        public void RealEngineM3P1ContractMapsClearAndNotSwapIntoFakeCue()
        {
            string b64Id = Convert.ToBase64String(Encoding.UTF8.GetBytes("e1"));
            string b64Key = Convert.ToBase64String(Encoding.UTF8.GetBytes("tile.gem.猫"));
            string rows = "1|"+b64Id+"|1|"+b64Key+"|1|0:0:1\n"+
                          "2|"+b64Id+"|0|"+b64Key+"|1|0:1:1\n";
            var events = VufCrossFactoryContractWindow.ParseEvents(
                Wire(rows,2), Parse());
            Assert.That(events.Count, Is.EqualTo(2));
            Assert.That(events[0].VufEvent, Is.EqualTo("tile_match"));
            Assert.That(events[1].VufEvent, Is.Null,
                "Engine Swap has no confirmed original VUF animation cue");
            Assert.That(events[0].Cells[0], Is.EqualTo(new Vector3Int(1,0,0)));
        }

        [Test]
        public void TamperedReceiptAndOutOfBoardEngineEventsFailClosed()
        {
            string id = Convert.ToBase64String(Encoding.UTF8.GetBytes("e1"));
            string key = Convert.ToBase64String(Encoding.UTF8.GetBytes("board.one"));
            byte[] valid = Wire("1|"+id+"|1|"+key+"|1|0:0:0\n",1);
            valid[valid.Length-1] = (byte)'0';
            Assert.Throws<FormatException>(() =>
                VufCrossFactoryContractWindow.ParseEvents(valid,Parse()));
            Assert.Throws<FormatException>(() =>
                VufCrossFactoryContractWindow.ParseEvents(
                    Wire("1|"+id+"|1|"+key+"|1|0:8:0\n",1),Parse()));
        }

        [Test]
        public void ActualUnityGridIsOnlyTemporaryRealDraftIdentifiers()
        {
            var level = Parse();
            var board = VufCrossFactoryContractWindow.BuildRealDraftBoard(level);
            try
            {
                Assert.That(board.GetComponent<Canvas>(), Is.Not.Null);
                Assert.That(board.hideFlags & HideFlags.DontSaveInEditor,
                    Is.Not.EqualTo(HideFlags.None));
                var labels=board.GetComponentsInChildren<Text>(true);
                Assert.That(labels.Length, Is.EqualTo(4));
                Assert.That(labels[0].text, Is.EqualTo("gem.猫"));
                Assert.That(labels[2].text, Is.EqualTo("HOLE"));
            }
            finally { UnityEngine.Object.DestroyImmediate(board); }
        }
    }
}
